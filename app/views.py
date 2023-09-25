from ast import In
import json
from django.shortcuts import redirect, render
from django.http import HttpResponse
from app.chatbot_project.chat import chat 
from .models import Group, Intent, Pattern, Response, Chats
import os
from django.conf import settings



# Chat url
def index(request):
    Chats.objects.create(chat = "")
    id = Chats.objects.latest('id').pk
    file_path = os.path.join(settings.BASE_DIR, 'app', 'chatbot_project', 'files', str(id) + '.txt')
    old_file_path = os.path.join(settings.BASE_DIR, 'app', 'chatbot_project', 'files', str(id-1) + '.txt')
    f = open(file_path, "w+")

    # delete empty files 
    if id > 0:
        if os.stat(old_file_path).st_size == 0:
            os.remove(old_file_path)
            Chats.objects.get(pk=id-1).delete()
    
    return render(request, './views/index.html', {"chat_id": id})

# post function for real time chat
def send(request):
    print(request.POST)
    message = request.POST['message']
    chat_answer = chat(message, request.POST['chatID'])
    return HttpResponse(chat_answer)

# database management site
#######

def datasheet(request):
    # global variables
    groups = []
    err = 'no_error'
    if 'group' in request.session:
        del request.session['group']

    # post methods
    if request.method == 'POST':

        # create new group
        if request.POST['post-function'] == 'new-group':
            try:
                request.session['error'] = 'This Group already exists'
                Group.objects.get(name = request.POST['groupName'])
            except Group.DoesNotExist:
                request.session['error'] = 'no_error'
                Group.objects.create(name = request.POST['groupName'])
            
        # edit group name
        if request.POST['post-function'] == 'edit-group':
            changings = json.loads(request.POST['editedGroups'])

            for change in changings:
                Group.objects.filter(pk=change['id']).update(name=change['new_line'])

        # delete group 
        if request.POST['post-function'] == 'delete-group':
            group_name = request.POST['groupName']
            Intent.objects.filter(group_id = Group.objects.get(name=group_name).pk).update(group_id=-1)
            Group.objects.filter(name=group_name).delete()

        # show group intents
        if request.POST['post-function'] == 'details-group':
            group_name = request.POST['showIntents']
            request.session['group'] = group_name
            return redirect('intents')


    all_groups = Group.objects.values_list('id', 'name')
    for group in all_groups:
        groups.append({"id": group[0], "name": group[1]})
   
    # error handling
    if request.method == 'GET':
        if 'error' not in request.session:
            err = 'no_error'
        else:
            err = request.session['error']
            del request.session['error'] 
    return render(request, './views/datasheet.html', {"all_groups": groups, "error": err})

def intents(request):
    if 'group' not in request.session:
        return redirect('../')
    err = "no_error"
    intents_list = []
    groups = []
    group_name = request.session['group']

     # post methods
    if request.method == 'POST':

        # create new intent
        if request.POST['post-function'] == 'new-intent':
            try:
                request.session['error'] = "This Intent already exists"
                Intent.objects.get(name = request.POST['intentName'])
            except Intent.DoesNotExist:
                request.session['error'] = 'no_error'
                if group_name == 'groupless':
                    group_id = -1
                else:
                    group_id = Group.objects.get(name=group_name).pk
                Intent.objects.create(name = request.POST['intentName'], group_id=group_id)

        # edit intents
        if request.POST['post-function'] == 'edit-intent':
            changings = json.loads(request.POST['editedIntents'])

            for change in changings:
                Intent.objects.filter(pk=change['id']).update(name=change['new_line'])

        #delete intents
        if request.POST['post-function'] == 'delete-intent':
            intent_name = request.POST['intentName']
            Intent.objects.filter(name=intent_name).delete()

        #assign intent to group
        if request.POST['post-function'] == 'assign-intent':
            intent_name = request.POST['intentName']
            group_name = request.POST['groupName']

            if group_name == 'none':
                Intent.objects.filter(name=intent_name).update(group_id = -1)
            else:
                group_id = Group.objects.get(name=group_name).pk
                Intent.objects.filter(name=intent_name).update(group_id = group_id)

        #show intent details
        if request.POST['post-function'] == 'details-intent':
            intent_name = request.POST['showPatterns']
            request.session['intent'] = intent_name
            return redirect('patterns')
    
    # get data for viewing data
    if group_name == 'groupless':
        group_id = -1
    else:
        group_id = Group.objects.get(name=group_name).pk
    intents = Intent.objects.values_list('id', 'name').filter(group_id=group_id)

    for intent in intents:
        intents_list.append({"id": intent[0], "intent": intent[1]})

    all_groups = Group.objects.values_list('id', 'name')
    for group in all_groups:
        groups.append({"id": group[0], "name": group[1]})

    # error handling
    if request.method == 'GET':
        if 'error' not in request.session:
            err = 'no_error'
        else:
            err = request.session['error']
            del request.session['error'] 
    
    return render(request, './views/intents.html', {"all_intents": intents_list, "all_groups": groups, "error": err, "group_name": group_name})

def patterns(request):
    if 'intent' not in request.session:
        return redirect('../')
    err = 'no_error'
    patterns_list = []
    responses_list = []
    intent_name = request.session['intent']
    intent_id = Intent.objects.get(name=intent_name).pk


    # post methods
    if request.method == 'POST':

        # create new pattern
        if request.POST['post-function'] == 'new-pr':
            pr = request.POST['pr']
            text = request.POST['text']
            if text[0] == '"' and text[-1] == '"':
                print("Test")
                text = text[:0] + "" + text[1:]
                text = text[:-1] + "" + text[0:]
            if pr == 'patterns':
                try:
                    request.session['error'] = 'This Pattern already exists'
                    Pattern.objects.get(name = text)
                except Pattern.DoesNotExist:
                    request.session['error'] = 'no_error'
                    Pattern.objects.create(name = text, intent_id=intent_id)
            if pr == 'responses':
            
                try:
                    request.session['error'] = 'This Response already exists'
                    Response.objects.get(name = text)
                except Response.DoesNotExist:
                    request.session['error'] = 'no_error'
                    intent_id = Intent.objects.get(name=intent_name).pk
                    Response.objects.create(name = text, intent_id=intent_id)

        # edit patterns
        if request.POST['post-function'] == 'edit-pr':
            try:
                changings_p = json.loads(request.POST['changings_p'])
                for change in changings_p:
                    Pattern.objects.filter(pk=change['id']).update(name=change['new_line'])
            except json.JSONDecodeError: 
                pass
            try:
                changings_r = json.loads(request.POST['changings_r'])
                for change in changings_r:
                    Response.objects.filter(pk=change['id']).update(name=change['new_line'])
            except json.JSONDecodeError:
                pass
        
        # delete pattern
        if request.POST['post-function'] == 'delete-pattern':
            pattern_name = request.POST['pattern']
            Pattern.objects.filter(name=pattern_name).delete()

        # delete response
        if request.POST['post-function'] == 'delete-response':
            response_name = request.POST['response']
            print(response_name)
            Response.objects.filter(name=response_name).delete()

    patterns = Pattern.objects.values_list('id', 'name').filter(intent_id=intent_id)
    responses = Response.objects.values_list('id', 'name').filter(intent_id=intent_id)

    for pattern in patterns:
        patterns_list.append({"id": pattern[0], "text": pattern[1]})
    for response in responses:
        responses_list.append({"id": response[0], "text": response[1]})
    
    # error handling
    if request.method == 'GET':
        if 'error' not in request.session:
            err = 'no_error'
        else:
            err = request.session['error']
            del request.session['error'] 

    return render(request, './views/patterns.html', {'error': err, 'all_patterns': patterns_list, 'all_responses': responses_list, "intent_name": intent_name})