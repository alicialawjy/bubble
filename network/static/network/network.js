////////////////////////////////////////////////////////////////////
///////////////////////  SUBMIT NEW POSTS   ////////////////////////
////////////////////////////////////////////////////////////////////

//----------------------- (i) via main page ----------------------//
document.addEventListener('DOMContentLoaded', function(){
    //Prevent submitting empty post
    const submit = document.querySelector('#submit_new');
    const textarea = document.querySelector('#textarea_new');
    const form = document.querySelector('#new_post');

    //By default, submit button is disabled
    submit.disabled = true;
    //Enable submission only when a key has been pressed
    stop_empty_posts(submit, textarea);
    
    //If submit the form
    form.addEventListener('submit', function() {submit_new(textarea)});
});


//------------ (ii) via New Bubble button (sidebar) ---------------//
document.addEventListener('DOMContentLoaded', function(){
    //When 'New Bubble'button is clicked, 
    document.querySelector('#new_bubble').onclick = function() {
        //Call the overlay
        call_overlay();
        document.querySelector('#overlay_heading').innerHTML = 'New Post';
        //If submit the form
        const form = document.querySelector('#overlay_form');
        const textarea = document.querySelector('#overlay_text');
        form.addEventListener('submit', function() {submit_new(textarea)});
    };
});

//-------------- NEW POST FUNCTION: CREATE POST INSTANCE --------------//
//Input: textarea element
function submit_new(textarea) {
    //Send a POST request of new post
    fetch('/new', {
        method:'POST',
        body: JSON.stringify({
            content: textarea.value
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.message) {
            console.log(result.message);
        } 
    })

    location.reload()
    //Stop the form from submitting
    return false
};

////////////////////////////////////////////////////////////////////
///////////////////         EDIT POST       ////////////////////////
////////////////////////////////////////////////////////////////////
document.addEventListener('DOMContentLoaded', function(){
    //Handle edit button: when clicked, show overlay page with textbox
    document.querySelectorAll('.edit_button').forEach(function(edit){
        edit.onclick= function(event) {
            const id = edit.dataset.post_id;
            const form = document.querySelector('#overlay_form');

            //Stop bubbling to <div>
            event.stopPropagation();

            call_overlay();
            //Overlay heading
            document.querySelector('#overlay_heading').innerHTML = 'Update';

            //Put text in the textarea
            document.querySelector('#overlay_text').innerHTML = document.querySelector(`#post_content${id}`).innerHTML;

            //If submit the form - use submit_edit
            form.addEventListener('submit', function() {submit_edit(id)});
        };
    });
});

//------------------ EDIT FUNCTION: PROCESS EDITED POST ------------------//
function submit_edit(id) {
    //Take the content from the text area
    const updated_content = document.querySelector('#overlay_text').value;
    //Send a put request to change the content
    fetch(`/post/${id}`, {
        method:'PUT',
        body: JSON.stringify({
            content: updated_content
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.message) {
            console.log(result.message);
        } 
    })

    //Replace the item in HTML first, no need to reload the page
    document.querySelector(`#post_content${id}`).innerHTML = updated_content;
    //Close the overlay
    document.querySelector('#overlay').style.display='none';

    //Stop the form from submitting
    return false
};


////////////////////////////////////////////////////////////////////
///////////////////////  REPLY ON POST  ////////////////////////////
////////////////////////////////////////////////////////////////////
document.addEventListener('DOMContentLoaded', function(){
    document.querySelectorAll('.reply_icon').forEach(function(reply) {
        reply.onclick = function(event) {
            const replied_to_id = reply.dataset.post_id; //The id of the post this reply was made to
            const form = document.querySelector('#overlay_form');
            const textarea = document.querySelector('#overlay_text');

            //Stop bubbling to <div>
            event.stopPropagation();

            if (authenticated === 'True') {
                call_overlay();
                //Overlay heading
                document.querySelector('#overlay_heading').innerHTML = 'Reply';

                //If submit the form:
                form.addEventListener('submit', function() {
                    //(i) Create it as a new post instance, and then 
                    //(ii) link it with the post it was replying to
                    link_reply(replied_to_id, textarea);
                });
            }
        };
        
    });
});

//------------------ REPLY ONLY FUNCTION: LINK REPLY TO POST ------------------//
function link_reply(replied_to_id, textarea) {
    //Create a new post instance (POST request)
    fetch('/new', {
        method:'POST',
        body: JSON.stringify({
            content: textarea.value
        })
    })
    .then(response => response.json())
    .then(result => {
        //Once new post created, link it to the post it was replying (PUT request)
        var replied_by_id = result.id_created;
        console.log(`post created id = ${replied_by_id}`)
        return fetch(`/post/${replied_to_id}`, {
            method:'PUT',
            body: JSON.stringify({
                reply: replied_by_id
            })
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.message) {
            console.log(result.message);
        } 
    })
    
    
    //Refresh the page
    location.reload()
    //Increase the reply count
    document.querySelector(`#reply_count${replied_to_id}`).innerHTML ++;

    //Stop the form from submitting
    return false
}

////////////////////////////////////////////////////////////////////
/////////////////////         FOLLOW       /////////////////////////      
////////////////////////////////////////////////////////////////////
document.addEventListener('DOMContentLoaded', function(){
    const follow_button = document.querySelector('#follow_button');
    const profile_username = document.querySelector('#profile_owner').innerHTML;

    follow_button.addEventListener('click',function() {
        if (follow_button.innerHTML === 'Follow') {
            //Add to the profile owner's follow count: send a PUT request
            fetch(`/user/${curr_user}`, {
                method:'PUT',
                body: JSON.stringify({
                    follow: profile_username
                })
            })

            //and, Change follow button to an unfollow button
            follow_button.innerHTML = 'Unfollow';
            document.querySelector('#profile_follower').innerHTML ++;

        }
        else {
            //Add to the profile owner's follow count: send a PUT request
            fetch(`/user/${curr_user}`, {
                method:'PUT',
                body: JSON.stringify({
                    unfollow: profile_username
                })
            })
            //and, Change unfollow button to a follow button
            follow_button.innerHTML = 'Follow';
            document.querySelector('#profile_follower').innerHTML --;
        }
    });
});

////////////////////////////////////////////////////////////////////
////////////////////////         LIKES       ///////////////////////      
////////////////////////////////////////////////////////////////////
document.addEventListener('DOMContentLoaded', function(){
    //Look at all like buttons
    document.querySelectorAll('.heart_icon').forEach(function(button){
        //If the page is loaded with post liked, the heart button should remain pink
        if (button.dataset.liked === 'true') {
            button.style.background = 'pink';
        }
        //If any of the buttons are clicked, execute the like_post function for that post
        button.onclick = function(event) {
            if (authenticated === 'True') {
                like_post(button)
            }
            //Stop bubbling to <div>
            event.stopPropagation();
        };
    });
});

//-------------- LIKE FUNCTION: PROCESS LIKES/UNLIKES ------------//
function like_post(button) {
    const id = button.dataset.post_id;
    //If the button's background is not pink (aka post was not liked before)
    if (button.dataset.liked === 'false') {
        //Send a PUT request to add a like to the post
        fetch(`/post/${id}`, {
            method:'PUT',
            body: JSON.stringify({
                like: true
            })
        })
        //Change the background color after clicked
        button.style.background = 'pink';
        //Increase the like count
        document.querySelector(`#like_count${id}`).innerHTML ++;
        //Change the data
        button.dataset.liked = 'true';
    }

    else {
        //Send a PUT request to unlike the post
        fetch(`/post/${button.dataset.post_id}`, {
            method:'PUT',
            body: JSON.stringify({
                like: false
            })
        })
        //Change the background color after clicked
        button.style.background = 'none';
        //Decrease the like count
        document.querySelector(`#like_count${id}`).innerHTML --;
        //Change the data
        button.dataset.liked = 'false';
    }
}

////////////////////////////////////////////////////////////////////
/////////////////         CLICK ON POST      ///////////////////////      
////////////////////////////////////////////////////////////////////
document.addEventListener('DOMContentLoaded', function(){
    //Look at all like posts
    document.querySelectorAll('.post').forEach(function(post){
        post.onclick = function() {
            const post_id = post.dataset.post_id;
            window.location.href = `/post/${post_id}`;
        };
    });
});

////////////////////////////////////////////////////////////////////
///////////////////////  OTHER FUNCTIONS  //////////////////////////
////////////////////////////////////////////////////////////////////

//------------------------ CALL OVERLAY -----------------------//
function call_overlay() {
    //Make overlay visible: display=block
    document.querySelector('#overlay').style.display='block';

    //Close overlay if x clicked: aka display=none
    document.querySelector('#close_button').addEventListener('click', function(){
        document.querySelector('#overlay').style.display='none';
    });

    //Prevent submitting empty post
    const submit = document.querySelector('#overlay_button');
    const textarea = document.querySelector('#overlay_text');

    //By default, submit button is disabled
    submit.disabled = true;
    //Enable submission only when a key has been pressed
    stop_empty_posts(submit, textarea);

}

//--------------- STOP EMPTY POSTS FROM SUBMITTING --------------//
//Inputs: submit button, the text area element
function stop_empty_posts(submit, textarea) {
    textarea.onkeyup = () => {
        //If there's text in the text area, enable
        if (textarea.value.length > 0) {
            submit.disabled=false;
        }
        //Else, disable
        else {
            submit.disabled=true;
        }
    };
}

