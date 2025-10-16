"""
Views for the installations app
"""
from django.apps import apps
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Count
from django.db.models.fields import related
from django.forms import modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
import json
import time

# =================== IMPORT FROM OWN APPS ====================================
from basic.utils import ErrHandle
from basic.views import get_application_context
from utils import view_util, help_util 
from utils.view_util import Crud, Cruds, make_tabs, FormsetFactoryManager
from utils.model_util import copy_complete, identifiers2instances 
from utilities.search import Search


def ajax_identifiers_to_instances(request,identifiers):
    '''returns an instance based on identifier: app_name model_name and pk.
    e.g. installations_system_34
    '''
    if type(identifiers) == str:identifiers = identifiers.split(',')
    instances = identifiers2instances(identifiers)
    print(instances,'instances')
    d = [x.sidebar_info for x in instances]
    #d = serializers.serialize('json',instances)
    print(d,'serial')
    return JsonResponse({'instances':d})


def list_view(request, model_name, app_name, max_entries=500):
    '''list view of a model.'''

    response = None
    oErr = ErrHandle()
    try:
        extended_search = getextended_search(request)
        active_fields= get_active_search_buttons(request)
        special_terms= get_active_special_term_buttons(request)
        print(special_terms,999)
        s = Search(request,model_name,app_name,active_fields=active_fields,
            special_terms = special_terms, max_entries = max_entries)
        instances= s.filter()
        print('done filtering')

        # Special processing for aggregate counts
        if s and s.query:
            if model_name == "Purpose" and "installationcount" in s.query.order.order_by:
                instances = instances.annotate(installationcount=Count('installation__purposes'))
            elif model_name == "Literature" and "eventcount" in s.query.order.order_by:
                instances = instances.annotate(eventcount=Count('eventliteraturerelation'))
        
        print('empty query:',s.query.empty)
        name = handle_model_page_name(model_name)
        model = apps.get_model(app_name,model_name)
        plural_name = model._meta.verbose_name_plural
        var = {model_name.lower() +'_list':instances,
            'page_name':name,
            'order':s.order.order_by,'direction':s.order.direction,
            'app_name':app_name,
            'plural_name': plural_name,
            'query':s.query.query,'nentries':s.nentries,
            'search_fields':s.search_fields,
            'name':model_name.lower(),'extended_search':extended_search,
            'active_search_buttons':active_fields,
            'active_special_term_buttons':special_terms}
        context = get_application_context(request, var)
        print(s.notes,000,'<----')
        response = render(request, app_name+'/'+model_name.lower()+'_list.html',context)
    except:
        msg = oErr.get_error_message()
        oErr.DoError("utilities/list_view")
    return response


@permission_required('utilities.add_generic')
def edit_model(request, name_space, model_name, app_name, instance_id = None, 
    formset_names='', focus='default', view ='complete', before_save = None, related_objects=None):
    '''edit view generalized over models.
    assumes a 'add_{{model_name}}.html template and edit_{{model_name}} function
    and {{model_name}}Form
    '''

    start = time.time()
    names = formset_names
    oErr = ErrHandle()
    response = None
    try:
        # Get the model form
        model = apps.get_model(app_name,model_name)
        modelform = view_util.get_modelform(name_space,model_name+'Form')
        print('get model and form',delta(start))

        # Get the instance and the relevant CRUD
        instance= model.objects.get(pk=instance_id) if instance_id else None
        crud = Crud(instance) if instance and model_name != 'Location' else None
        print('get crud',delta(start))

        # Get the initial context for authorization purposes
        context = get_application_context(request, {})

        # Do not allow non-editors to ADD a new item
        if instance_id is None and not context['is_app_editor']:
            # This is a non-editor attempting to create a new instance: do not allow this
            response = redirect(reverse('npermission'))
        else:

            # Process POST form - if this is a POST one
            ffm, form = None, None
            if request.method == 'POST' and context['is_app_editor']:
                focus, button = getfocus(request), getbutton(request)
                if button in 'delete,cancel,confirm_delete': 
                    return delete_model(request,model_name,app_name,instance_id)
                copy_instance = copy_complete(instance) if button == 'saveas' and instance else False
                form = modelform(request.POST, request.FILES, instance=instance)
                print('made form in post',delta(start))
        
                if form.is_valid() or copy_instance:
                    print('form is valid: ',form.cleaned_data,type(form))

                    # Allow the user to add something before actually saving
                    if not before_save is None:
                        before_save(form, instance)

                    # Determine what the instance will be
                    if not button == 'saveas':
                        instance = form.save()
                    else:
                        instance = copy_instance
                    if view == 'complete':
                        ffm = FormsetFactoryManager(name_space,names,request,instance)
                        valid = ffm.save()
                        print('formset factory manager / form making done',delta(start))
                        if valid:
                            print('validated form',delta(start))
                            show_messages(request,button, model_name)
                            if button== 'add_another':
                                return HttpResponseRedirect(
                                    reverse(app_name+':add_'+model_name.lower()))
                            elif button == 'show_view':
                                return HttpResponseRedirect(
                                    reverse("{}:{}-detail".format(app_name, model_name.lower()), kwargs={'pk': instance.pk}))
                                    # reverse(app_name+':detail_'+model_name.lower()))
                            elif button == "save_view":
                                url = reverse("{}_details".format(model_name.lower()), kwargs={'pk': instance.pk})
                                return HttpResponseRedirect(url)
                            return HttpResponseRedirect(reverse(
                                app_name+':edit_'+model_name.lower(), 
                                kwargs={'pk':instance.pk,'focus':focus}))
                        else: print('ERROR',ffm.errors)
                    else: return HttpResponseRedirect('/utilities/close/')
                else:
                    nfe = form.non_field_errors()
                    if len(nfe) == 0:
                        # Use form.errors instead
                        nfe = [ "{}: {}".format(k, v) for k,v in form.errors.items() ]
                    print('form invalid:',nfe)
                    show_messages(request,'form_invalid', model_name, form)
                    x = form['start_date'].errors
            print('post part done',delta(start))

            # Adapt forms (post-POST)
            if not form: form = modelform(instance=instance)
            if not ffm: ffm = FormsetFactoryManager(name_space,names,instance=instance)
            print('(after post formset factory manager / form making done',delta(start))

            # Create tabs
            tabs = make_tabs(model_name.lower(), focus_names = focus)
            print('tabs made',delta(start), tabs)

            # Figure out correct page name
            name = handle_model_page_name(model_name)
            page_name = 'Edit ' +name if instance_id else 'Add ' +name

            # Create helper
            helper = help_util.Helper(model_name=model_name)
            print('helper made',delta(start))

            # Collect the context
            if instance_id is None:
                related_objects = None
            args = {'form':form,'page_name':page_name,'crud':crud,'model_name':model_name,
                'app_name':app_name,'tabs':tabs, 'view':view,'helper':helper.get_dict(),
                'instance':instance, 'related_objects': related_objects}
            args.update(ffm.dict)
            # context = get_application_context(request, args)
            context.update(args)
            print('arg made, start rendering',delta(start))

            template_name = "{}/add_{}.html".format(app_name, model_name.lower())

            # Old: response = render(request,app_name+'/add_' + model_name.lower() + '.html',context)
            response = render(request, template_name, context)
    except:
        msg = oErr.get_error_message()
        oErr.DoError("edit_model")

    return response
        

@permission_required('utilities.add_generic')
def add_simple_model(request, name_space,model_name,app_name, page_name, pk = None):
    '''Function to add simple models with only a form could be extended.
    request     django object
    name_space  the name space of the module calling this function (to load forms / models)
    model_name  name of the model
    app_name    name of the app
    page_name   name of the page
    The form name should be of format <model_name>Form
    '''

    response = None
    oErr = ErrHandle()
    try:
        model = apps.get_model(app_name,model_name)
        modelform = view_util.get_modelform(name_space,model_name+'Form')
        instance= model.objects.get(pk=pk) if pk else None
        # form = modelform(request.POST)
        form = None
        if request.method == 'POST':
            form = modelform(request.POST, instance=instance)
            button = getbutton(request) 
            if button in 'delete,confirm_delete':
                print('deleting simple model')
                return delete_model(request,name_space,model_name,app_name,pk,True)
            if form.is_valid():
                form.save()
                messages.success(request, model_name + ' saved')
                return HttpResponseRedirect('/utilities/close/')
        if not form: form = modelform(instance=instance)
        instances = model.objects.all().order_by('name')
        page_name = 'Edit ' +model_name.lower() if pk else 'Add ' +model_name.lower()
        url = '/'.join(request.path.split('/')[:-1])+'/' if pk else request.path
        var = {'form':form, 'page_name':page_name, 'instances':instances, 'url':url}
        context = get_application_context(request, var)
        response = render(request, 'utilities/add_simple_model.html',context)
    except:
        msg = oErr.get_error_message()
        oErr.DoError("add_simple_model")

    return response


@permission_required('utilities.delete_generic')
def delete_model(request, model_name, app_name, pk, close = False):

    response = None
    oErr = ErrHandle()
    try:
        model = apps.get_model(app_name,model_name)
        instance= get_object_or_404(model,id =pk)
        focus, button = getfocus(request), getbutton(request)
        if request.method == 'POST':
            if button == 'cancel': 
                show_messages(request,button, model_name)
                return HttpResponseRedirect(reverse(
                    app_name+':edit_'+model_name.lower(), 
                    kwargs={'pk':instance.pk,'focus':focus}))
            if button == 'confirm_delete':
                instance.delete()
                show_messages(request,button, model_name)
                if close: return HttpResponseRedirect('/utilities/close/')
                url = '/utilities/list_view/'+model_name.lower()+'/' +app_name
                return HttpResponseRedirect(url)
        info = instance.info
        var = {'info':info,'page_name':'Delete '+model_name.lower()}
        context = get_application_context(request, var)
        response = render(request, 'utilities/delete_model.html',context)
    except:
        msg = oErr.get_error_message()
        oErr.DoError("delete_model")

    return response
    

def getfocus(request):
    '''extracts focus variable from the request object to correctly set the active tabs.'''
    if 'focus' in request.POST.keys():
        focus = request.POST['focus']
        if focus == '': return 'default'
        else: return focus
    else: return 'default'

# Create your views here.
def getbutton(request):
    if 'save' in request.POST.keys():
        return request.POST['save']
    else: return 'default'


def getextended_search(request):
    print(request.GET)
    if 'extended_search' in request.GET.keys():
        return request.GET['extended_search']
    else: return 'display:block'


def get_active_search_buttons(request):
    print(request.GET)
    if 'active_search_buttons' in request.GET.keys():
        return request.GET['active_search_buttons'].split(',')
    else: return []


def get_active_special_term_buttons(request):
    print(request.GET)
    if 'active_special_term_buttons' in request.GET.keys():
        return request.GET['active_special_term_buttons'].split(',')
    else: return []


def show_messages(request,message_type,model_name,form=None):
    '''provide user feedback on submitting a form.'''

    oErr = ErrHandle()
    try:
        print(message_type)
        if message_type == 'saveas':messages.warning(request,
            'saved a copy of '+model_name+'. Use "save" button to store edits to this copy')
        elif message_type == 'confirm_delete':messages.success(request, model_name + ' deleted')
        elif message_type == 'cancel':messages.warning(request,'delete aborted')
        elif message_type == 'form_invalid':
            for error in form.non_field_errors():
                messages.warning(request,error)
        else: messages.success(request, model_name + ' saved')
    except:
        msg = oErr.get_error_message()
        oErr.DoError("show_messages")


def close(request):
    '''page that closes itself for on the fly creation of model instances 
    (loaded in a new tab).'''
    return render(request,'utilities/close.html')


def delta(start):
    return time.time() - start


def handle_model_page_name(model_name):
    d ={'eventtype':'event type','eventrole':'event role','texttype':'text type'}
    d['institutiontype']= 'intitution type'
    name = model_name.lower()
    if name in d.keys():name = d[name]
    return name
