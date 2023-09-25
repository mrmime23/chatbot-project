
$(document).on('submit','#post-message', function(e){
    e.preventDefault();
    create_question($('#message').val())
    $.ajax({
        type: 'POST',
        url: '/send',
        data:{
            message:$('#message').val(),
            chatID: chat_id,
            csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
        },
        success: function(data){
            
            setTimeout(function () {
                create_answer(String(data))
            }, 250)
        },
        error: function () {
            console.log('Failed ');
            console.log(error)
           }
    });
    document.getElementById('message').value = ''
});

function create_question(text){
    
    parent = document.getElementsByClassName('chat')[0]
    chat_field = document.createElement('div')
    chat_field.classList.add('chat-message')
    chat_field.classList.add('you')

    messenger = document.createElement('p')
    messenger.classList.add('from')
    messenger.innerHTML = "You: "
    
    content = document.createElement('p')
    content.classList.add('message-content')
    content.innerHTML = text

    chat_field.appendChild(messenger)
    chat_field.appendChild(content)
    parent.appendChild(chat_field)
    scroll_down()
}

function create_answer(text){
    parent = document.getElementsByClassName('chat')[0]
    chat_field = document.createElement('div')
    chat_field.classList.add('chat-message')
    chat_field.classList.add('bot')

    messenger = document.createElement('p')
    messenger.classList.add('from')
    messenger.innerHTML = "Bot: "
    
    content = document.createElement('p')
    content.classList.add('message-content')
    content.innerHTML = urlify(text)

    chat_field.appendChild(messenger)
    chat_field.appendChild(content)
    parent.appendChild(chat_field)
    scroll_down()
}

function scroll_down(){
    let scrollbar = document.getElementsByClassName('chat')[0]
    scrollbar.scrollTop = scrollbar.scrollHeight - scrollbar.clientHeight
}

function urlify(text) {
    var urlRegex = /(https?:\/\/[^\s]+)/g;
    return text.replace(urlRegex, function(url) {
      return '<a href="' + url + '">' + url + '</a>';
    })
  }