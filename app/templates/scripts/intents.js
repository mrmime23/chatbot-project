let modal1 = document.getElementById("myModal");
let btn1 = document.getElementById("add-new-intent");
let span1 = document.getElementsByClassName("close")[0];
let list = document.getElementById('faq-list');
let edit_button = document.getElementById('edit-intent');
let dropdown = document.getElementById('group-dropdown');

let changed_intents = [];
let intents_list = [], id = [];
btn1.onclick = function () {
    modal1.style.display = "block";
};

span1.onclick = function () {
    modal1.style.display = "none";
};


window.onclick = function (event) {
    if (event.target == modal1) {
        modal1.style.display = "none";
    }
    if (event.target == modal2) {
        modal2.style.display = "none";
    }
}


if(intents.length >0){
    for(let i = 0; i<intents.length; i++){
        intents_list.push(intents[i].intent);
        id.push(intents[i].id)
    }           
}else{
    document.getElementsByClassName('faq')[0].style.height = "100px"
}


for(let i = 0; i<intents_list.length; i++){
    let new_but = document.createElement("input");
    new_but.type = "button"
    new_but.id=i
    new_but.value = intents_list[i]
    new_but.className = "intents-details"
    new_but.onchange = change_intents
    new_but.onpropertychange = change_intents;
    new_but.onkeyuponpaste = change_intents;
    new_but.oninput = change_intents;
    let new_li = document.createElement("li");
    new_li.className = "intents"
    new_li.appendChild(new_but);
    
    let admin = document.createElement('button');
    admin.type = "button"
    admin.id = intents_list[i];
    admin.className = "add-group"
    let plus = document.createElement('i');
    plus.className = "fa-solid"
    plus.classList.add("fa-plus");
    admin.appendChild(plus);
    new_li.appendChild(admin);

    let new_button2 = document.createElement('button');
    new_button2.name = "intent";
    new_button2.className = "deleteintents-button";
    new_button2.classList.add("deleting-intent");
    new_button2.value = intents_list[i];
    let new_trash = document.createElement('i');
    new_trash.className = "fa-solid";
    new_trash.classList.add("fa-trash");
    new_button2.appendChild(new_trash);
    new_li.appendChild(new_button2);

    list.appendChild(new_li);
}


let admin_buttons = document.getElementsByClassName('add-group');

//edit
let on_edit_mode = 0
edit_button.onclick = function(){
    let edit_button_text = (on_edit_mode == 0) ? edit_button.innerHTML = "Cancel" : edit_button.innerHTML = "Edit";
    let elements_for_change = document.getElementById('faq-list').children;
    let trash = document.getElementsByClassName("deleteintents-button");
    for(let i = 0; i<elements_for_change.length; i++){
        
        if(elements_for_change[i].children[0].type == "button"){
            elements_for_change[i].children[0].type = "text";
            on_edit_mode = 1;
            document.getElementById('submit-edit').style.display = "inline"
            trash[i].style.display = "inline";
            admin_buttons[i].style.display = "inline";
        }else{
            elements_for_change[i].children[0].type = "button";
            document.getElementById('submit-edit').style.display = "none"
            on_edit_mode = 0;
            trash[i].style.display = "none";
            admin_buttons[i].style.display = "none";
        }
    }
}


function change_intents() {
    if (intents[this.id].intent != this.value) {    //check if the value changed
        if (changed_intents.length != 0) {   //check if any changings are included to the array
            for (let i = 0; i < changed_intents.length; i++) {     //search for existing id to avoid duplicates
                if (changed_intents[i].id == id[this.id]) {
                    changed_intents.splice(i, 1);
                }
            }
            if (this.value != "") {
                changed_intents.push({ "id": id[this.id], "new_line": this.value })   //insert changed value
            }
        } else {
            if (this.value != "") {
                changed_intents.push({ "id": id[this.id], "new_line": this.value })   //insert changed value
            }
        }
    } else {
        if (changed_intents.length != 0) {
            for (let i = 0; i < changed_intents.length; i++) {
                if (changed_intents[i].id == id[this.id]) {
                    
                    changed_intents.splice(i, 1);
                }
            }
        }
    }
    document.getElementById('saved-intents').value = JSON.stringify(changed_intents);
}



for(let i = 0; i<admin_buttons.length; i++){
    admin_buttons[i].onclick = function(){
        
    }
}


let modal2 = document.getElementById("myModal2");
let span2 = document.getElementsByClassName("close")[1];
let btns = [];
for(let i = 0; i<intents.length; i++){
    btns[i] = document.getElementById(intents[i].intent)
}

for(let i = 0; i<intents.length; i++){
    btns[i].onclick = function(){
        modal2.style.display = "block";
        document.getElementById('assign-intent').value=intents[i].intent;
        document.getElementById('assign-intent-text').value = intents[i].intent;
        for(let x = 0; x<groups.length; x++){
            let opt = document.createElement('option');
            opt.value = groups[x].name;
            opt.innerHTML = groups[x].name;
            dropdown.appendChild(opt);
        }
    }
}

span2.onclick = function () {
    modal2.style.display = "none";
};

function filter_intents(){
    let val = document.getElementById('input-search-intents').value.toLowerCase();
    let counter = intents.length;
    let intents_titles = [];
    for(let i = 0; i<counter; i++){
        intents_titles.push(intents[i].intent.toLowerCase());
    }
    let matches = intents_titles.filter(s => s.includes(val));
    if(val ==""){
        for(let i = 0; i<counter; i++){
            list.children[i].style.display = ""
        }
    }
    for(let i = 0; i<counter; i++){
        let el = list.children[i].children[0].value
        if(matches.indexOf(el) == -1){
            list.children[i].style.display = "none"
        }else{
            list.children[i].style.display = ""
        }
    }
}


// POST FUNCTIONS

// create new intent 
document.getElementById('sub-new-intent').onclick = function(){
    let intent_name = document.getElementById('new-Data-intent').value;
    let formData = new FormData();

    formData.append('post-function', "new-intent");
    formData.append('intentName', intent_name);
    formData.append('csrfmiddlewaretoken', token);
    fetch('/datasheet/intents/', {
        method: 'POST',
        body: formData,
    }).then( () => {
        window.location.reload()
    });
}

// edit intents
document.getElementById('submit-edit').onclick = function(){
    let changings = document.getElementById('saved-intents').value
    let formData = new FormData();

    formData.append('post-function', "edit-intent");
    formData.append('editedIntents', changings);
    formData.append('csrfmiddlewaretoken', token);
    fetch('/datasheet/intents/', {
        method: 'POST',
        body: formData,
    }).then( () => {
        window.location.reload();
    });
}

// delete intent
let del_buttons = document.getElementsByClassName('deleteintents-button')
for(let i = 0; i<del_buttons.length; i++){
    del_buttons[i].onclick = function(){
       let intent_name = del_buttons[i].value
       let formData = new FormData();

        formData.append('post-function', "delete-intent");
        formData.append('intentName', intent_name);
        formData.append('csrfmiddlewaretoken', token);
        fetch('/datasheet/intents/', {
            method: 'POST',
            body: formData,
        }).then( () => {
            window.location.reload()
        })
    }
}

// assign intent to group
document.getElementsByClassName('assign-button')[0].onclick = function() {
    let intent_name = document.getElementById('assign-intent').value
    let group_name = document.getElementById('group-dropdown').value
    let formData = new FormData();

        formData.append('post-function', "assign-intent");
        formData.append('intentName', intent_name);
        formData.append('groupName', group_name);
        formData.append('csrfmiddlewaretoken', token);
        fetch('/datasheet/intents/', {
            method: 'POST',
            body: formData,
        }).then( () => {
            window.location.reload()
        })
}

// show intent details
let intent_buttons = document.getElementsByClassName("intents-details");
    for(let i = 0; i<intent_buttons.length; i++){
        intent_buttons[i].onclick = function(){
            if(intent_buttons[i].type == "button"){
                show_intents = intent_buttons[i].value
                let formData = new FormData();

                formData.append('post-function', "details-intent");
                formData.append('showPatterns', show_intents);
                formData.append('csrfmiddlewaretoken', token);
                fetch('/datasheet/intents/', {
                    method: 'POST',
                    body: formData,
                    redirect: 'follow'
                }).then( response => {
                    window.location.href = response.url
                })
            }
        }
    }