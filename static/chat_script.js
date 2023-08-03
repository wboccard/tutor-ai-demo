const record = document.querySelector('.record');
const stop = document.querySelector('.stop');
const chatlog = document.querySelector('.chat-log');

stop.disabled = true;

const sendAudioFile = file => {
  const formData = new FormData();
  formData.append('file', file, 'input.ogg');
  return fetch('/audioUpload', {
    method: 'POST',
    body: formData
  }).then((response) => response.text());
};

if (navigator.mediaDevices.getUserMedia) {
  console.log('getUserMedia supported.');

  const constraints = { audio: true };
  let chunks = [];

  let onSuccess = function(stream) {
    const mediaRecorder = new MediaRecorder(stream);

    record.onclick = function() {
      mediaRecorder.start();
      console.log(mediaRecorder.state);
      console.log("recorder started");
      record.style.background = "red";

      stop.disabled = false;
      record.disabled = true;
    }

    stop.onclick = function() {
      mediaRecorder.stop();
      console.log(mediaRecorder.state);
      console.log("recorder stopped");
      record.style.background = "";
      record.style.color = "";

      stop.disabled = true;
      record.disabled = false;
    }
    
    window.addEventListener('keydown', function(e) {
      if (e.key == " ") {
          if (!record.disabled){
            record.click()
          } else {
            stop.click()
          }
          console.log('Space pressed');
      }
    });

    mediaRecorder.onstop = async function(e) {
      console.log("data available after MediaRecorder.stop() called.");

      let blob = new Blob(chunks, { 'type' : 'audio/ogg; codecs=opus' });
      chunks = [];
      console.log("recorder stopped");

      speech_to_text = await sendAudioFile(blob);

      let response_row = document.createElement('tr');
      let response = document.createElement('td');
      let delete_button = document.createElement('button')
      let btn_holder = document.createElement('td');

      response_row.classList.add('response');
      response.textContent = speech_to_text;
      delete_button.textContent = 'X';
      delete_button.className = 'delete';
      
      btn_holder.appendChild(delete_button);
      response_row.appendChild(response);
      response_row.appendChild(btn_holder);
      chatlog.appendChild(response_row);

      delete_button.onclick = function(e){
        e.target.closest(".response").remove();
      }

      chat_response = await fetch('/askChat', {
        headers: {
          "Content-Type": "application/json"
        },
        method: 'POST',
        body: JSON.stringify({
          'question': speech_to_text
        })
      }).then((response) => response.text()).catch("An error occured.");

      speech_response = await fetch('/retrieveSpeech',{
        headers: {
          "Content-Type": "application/json"
        },
        method: 'POST',
        body: JSON.stringify({
          'text_to_speech': chat_response
        })
      }).then((response) => response.blob()).catch('An error occured.');
      
      let answer_row = document.createElement('tr');
      let answer = document.createElement('td');
      let answer_delete_button = document.createElement('button')
      let audio = document.createElement('audio');
      let answer_btn_holder = document.createElement('td');

      audio.setAttribute('style', 'display:none;');
      audio.setAttribute('autoplay', 'True');
      const audioURL = window.URL.createObjectURL(speech_response);
      audio.src = audioURL;

      answer.textContent = chat_response;
      answer_row.classList.add('response');
      answer_delete_button.textContent = 'X';
      answer_delete_button.className = 'delete';

      answer_btn_holder.appendChild(answer_delete_button);
      answer.appendChild(audio);
      answer_row.appendChild(answer);
      answer_row.appendChild(answer_btn_holder);
      chatlog.appendChild(answer_row);

      answer_delete_button.onclick = function(e){
        e.target.closest(".response").remove();
      }
      
      window.addEventListener('keyup', function(e) {
        if (e.key == "Delete") {
            chatlog.lastChild.lastChild.lastChild.click()
            console.log('Delete pressed');
        }
      });
    }

    mediaRecorder.ondataavailable = function(e) {
      chunks.push(e.data);
    }
  }

  let onError = function(err) {
    console.log('The following error occured: ' + err);
  }

navigator.mediaDevices.getUserMedia(constraints).then(onSuccess, onError);

} else {
   console.log('getUserMedia not supported on your browser!');
}