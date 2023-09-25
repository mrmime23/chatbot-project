let patterns_list = document.getElementById('patterns-list');
let responses_list = document.getElementById('responses-list');
let edit_buttons = document.getElementsByClassName('edit-button');

let modal1 = document.getElementById("myModal");
let btn1 = document.getElementById("add-new-pattern");
let btn2 = document.getElementById("add-new-response");
let span1 = document.getElementsByClassName("close")[0];

let clicked_btn;

let changed_patterns = [], changed_responses = [];


//creating elements for every pattern
for (let i = 0; i < patterns.length; i++) {
    let new_li = document.createElement('li');
    let new_input = document.createElement('span');
    new_input.role = "textbox";
    new_input.onchange = change_patterns
    new_input.onpropertychange = change_patterns;
    new_input.onkeyuponpaste = change_patterns;
    new_input.oninput = change_patterns;
    new_input.id = i;
    new_input.className = "faq-values";
    new_input.classList.add("none-textarea");
    new_input.classList.add("patterns-list-element")
    new_input.innerHTML = patterns[i];
    new_li.appendChild(new_input);

    let new_button2 = document.createElement('button');
    new_button2.name = "pattern";
    new_button2.className = "deletePatterns-button";
    new_button2.classList.add("deleting-faq");
    new_button2.value = patterns[i];
    let new_trash = document.createElement('i');
    new_trash.className = "fa-solid";
    new_trash.classList.add("fa-trash");
    new_button2.appendChild(new_trash);
    new_li.appendChild(new_button2);
    patterns_list.appendChild(new_li);
}

//creating elements for every response
for (let i = 0; i < responses.length; i++) {
    let new_li = document.createElement('li');
    let new_input = document.createElement('span');
    new_input.role = "textbox";
    new_input.onchange = change_responses
    new_input.onpropertychange = change_responses;
    new_input.onkeyuponpaste = change_responses;
    new_input.oninput = change_responses;
    new_input.id = i;
    new_input.className = "faq-values";
    new_input.classList.add("none-textarea");
    new_input.classList.add("responses-list-element")
    new_input.innerHTML = responses[i];
    new_li.appendChild(new_input);


    let new_button2 = document.createElement('button');
    new_button2.name = "response";
    new_button2.className = "deleteResponses-button";
    new_button2.classList.add("deleting-faq");
    new_button2.value = deleteText(responses[i]);
    let new_trash = document.createElement('i');
    new_trash.className = "fa-solid";
    new_trash.classList.add("fa-trash");
    new_button2.appendChild(new_trash);
    new_li.appendChild(new_button2);
    responses_list.appendChild(new_li);
}

function deleteText(text){
    let new_text = JSON.stringify(text)
    new_text = new_text.substring(1)
    new_text = new_text.substring(0, new_text.length-1)
    return new_text
}
//edit button
let on_edit_mode = [0,0]
for (let i = 0; i < edit_buttons.length; i++) {
    edit_buttons[i].onclick = function () {
        let elements_for_change = edit_buttons[i].parentElement.parentElement.children[2];
        let edit_button_text = (on_edit_mode[i] == 0) ? edit_buttons[i].innerHTML = "Cancel" : edit_buttons[i].innerHTML = "Edit";
        for (let j = 0; j < elements_for_change.childElementCount; j++) {
            if(i == 0){ //patterns
                let trash = document.getElementsByClassName("deletePatterns-button");
                if (elements_for_change.children[j].children[0].className == "faq-values none-textarea patterns-list-element") { //changing the span to a textbox
                    on_edit_mode[i] = 1;
                    elements_for_change.children[j].children[0].className = "faq-values textarea patterns-list-element";     
                    elements_for_change.children[j].children[0].setAttribute("contenteditable", "true");
                    trash[j].style.display = "inline";
                    elements_for_change.children[j].children[0].innerHTML = patterns[j];
                }else{ //changing textbox to span
                    on_edit_mode[i] = 0;
                    elements_for_change.children[j].children[0].className = "faq-values none-textarea patterns-list-element"; 
                    elements_for_change.children[j].children[0].setAttribute("contenteditable", "false");
                    trash[j].style.display = "none";
                    elements_for_change.children[j].children[0].innerHTML = patterns[j];
                }
            }
           
            if(i == 1){ //responses
                
                let trash = document.getElementsByClassName("deleteResponses-button");
                if (elements_for_change.children[j].children[0].className == "faq-values none-textarea responses-list-element") { //changing the span to a textbox
                    on_edit_mode[i] = 1;
                    elements_for_change.children[j].children[0].className = "faq-values textarea responses-list-element";     
                    elements_for_change.children[j].children[0].setAttribute("contenteditable", "true");
                    trash[j].style.display = "inline";
                    elements_for_change.children[j].children[0].innerHTML = responses[j];
                }else{ //changing textbox to span
                    on_edit_mode[i] = 0;
                    elements_for_change.children[j].children[0].className = "faq-values none-textarea responses-list-element"; 
                    elements_for_change.children[j].children[0].setAttribute("contenteditable", "false");
                    trash[j].style.display = "none";
                    elements_for_change.children[j].children[0].innerHTML = responses[j];
                }
            }
        }
        let submit_element = document.getElementById("submit-edit"); 
        let submit_button = (on_edit_mode.includes(1)) ? submit_element.style.display = "inline": submit_element.style.display = "none";
    }
}


let trash = document.getElementsByClassName("deleteResponses-button");
for(let x = 0; x<trash.length; x++){
    trash[x].style.display = "none";
}

//modals
btn1.onclick = function () {
    modal1.style.display = "block";
    clicked_btn = "pattern"
};

btn2.onclick = function () {
    modal1.style.display = "block";
    clicked_btn = "response"
}

span1.onclick = function () {
    modal1.style.display = "none";
};

//reformating the text of the new pr
function reformating_pr(){
    let el = document.getElementsByClassName("faq-values")[0];
    return deleteText(el.innerText || el.textContent)
}

window.onclick = function (event) {
    if (event.target == modal1) {
        modal1.style.display = "none";
    }
    if (clicked_btn == "pattern") {
        document.getElementById('PR-label').innerHTML = "Type a new pattern";
        document.getElementById('modal-create-headline').innerHTML = "Create new Pattern";
        document.getElementById('pr-name').value = "patterns"
    } else {
        document.getElementById('PR-label').innerHTML = "Type a new response";
        document.getElementById('modal-create-headline').innerHTML = "Create new Response";
        document.getElementById('pr-name').value = "responses"
    }
}


//from div form to \n form
function reformat(text){
    let el = text;
    var text1 = el.innerText || el.textContent;
  
    let a = text1.split("\n")
   
    for(let i = 0; i<a.length; i++){
        if(a[i] == ""){
            a.splice(i,1);
            i--
        }
    }
    a = a.join("\\n")
    
    return a;
}
//editing
function change_patterns() {
    let new_text = reformat(this)
    if (patterns[this.id] != new_text) {    //check if the value changed
        if (changed_patterns.length != 0) {   //check if any changings are included to the array
            for (let i = 0; i < changed_patterns.length; i++) {     //search for existing id to avoid duplicates
                if (changed_patterns[i].id == pat_id[this.id]) {
                    changed_patterns.splice(i, 1);
                }
            }
            if (new_text != "") {
                changed_patterns.push({ "id": pat_id[this.id], "new_line": new_text })   //insert changed value
            }
        } else {
            if (new_text != "") {
                changed_patterns.push({ "id": pat_id[this.id], "new_line": new_text })   //insert changed value
            }
        }
    } else {
        if (changed_patterns.length != 0) {
            for (let i = 0; i < changed_patterns.length; i++) {
                if (changed_patterns[i].id == pat_id[this.id]) {
                    changed_patterns.splice(i, 1);
                }
            }
        }
    }
    document.getElementById('saved-changes_patterns').value = JSON.stringify(changed_patterns);
}

function change_responses() {
    let new_text = reformat(this)

    if (responses[this.id] != new_text) {    //check if the value changed
        if (changed_responses.length != 0) {   //check if any changings are included to the array
            for (let i = 0; i < changed_responses.length; i++) {     //search for existing id to avoid duplicates
                if (changed_responses[i].id == res_id[this.id]) {
                    changed_responses.splice(i, 1);
                }
            }
            if (new_text != "") {
                changed_responses.push({ "id": res_id[this.id], "new_line": new_text })   //insert changed value
            }

        } else {
            if (new_text != "") {
                changed_responses.push({ "id": res_id[this.id], "new_line": new_text })   //insert changed value
            }
        }


    } else {
        if (changed_responses.length != 0) {
            for (let i = 0; i < changed_responses.length; i++) {
                if (changed_responses[i].id == res_id[this.id]) {
                    changed_responses.splice(i, 1);
                }
            }
        }
    }
    document.getElementById('saved-changes_responses').value = JSON.stringify(changed_responses);
}

//for the case, a tag has no patterns or responses
if(patterns.length == 0){
    patterns_list.style.height = "75px";
}
if(responses.length == 0){
    responses_list.style.height = "75px";
}



// POST Functions

//create new Pattern or Response
document.getElementById('create-pr').onclick = function () {
    let text = reformating_pr()
    let pr = document.getElementById('pr-name').value
    let formData = new FormData();

    formData.append('post-function', "new-pr");
    formData.append('text', text);
    formData.append('pr', pr);
    formData.append('csrfmiddlewaretoken', token);
    fetch('/datasheet/intents/patterns/', {
        method: 'POST',
        body: formData,
    }).then( () => {
        window.location.reload();
    });
}

// edit patterns
document.getElementById('submit-edit').onclick = function(){
    let changings_p = document.getElementById('saved-changes_patterns').value
    let changings_r = document.getElementById('saved-changes_responses').value
    let formData = new FormData();
    formData.append('post-function', "edit-pr");
    formData.append('changings_p', changings_p);
    formData.append('changings_r', changings_r);
    formData.append('csrfmiddlewaretoken', token);
    fetch('/datasheet/intents/patterns/', {
        method: 'POST',
        body: formData,
    }).then( () => {
        window.location.reload();
    });
}


// delete pattern
let del_pat = document.getElementsByClassName('deletePatterns-button')
for(let i = 0; i<del_pat.length; i++){
    del_pat[i].onclick = function(){
       let pattern_name = del_pat[i].value
       let formData = new FormData();

        formData.append('post-function', "delete-pattern");
        formData.append('pattern', pattern_name);
        formData.append('csrfmiddlewaretoken', token);
        fetch('/datasheet/intents/patterns/', {
            method: 'POST',
            body: formData,
        }).then( () => {
            window.location.reload()
        })
    }
}

// delete response
let del_resp = document.getElementsByClassName('deleteResponses-button')
for(let i = 0; i<del_resp.length; i++){
    del_resp[i].onclick = function(){
       let response_name = del_resp[i].value
       let formData = new FormData();

        formData.append('post-function', "delete-response");
        formData.append('response', response_name);
        formData.append('csrfmiddlewaretoken', token);
        fetch('/datasheet/intents/patterns/', {
            method: 'POST',
            body: formData,
        }).then( () => {
            window.location.reload()
        })
    }
}

