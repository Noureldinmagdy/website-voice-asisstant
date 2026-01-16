
/////////////////////////////////////
const config = {
    server_url: "http://localhost:3000",
    script_url: "http://localhost:3000/embed-popup.js"
}
//////////////////////////////////////

function randomId(prefix = "", len = 6) {
    return (
        prefix +
        Math.random().toString(36).substring(2, 2 + len)
    );
}

const room = randomId("room-");
const user = randomId("user-");

const script = document.createElement("script");
script.src = config.script_url;

script.setAttribute('data-lk-sandbox-id', config.server_url);
script.setAttribute('data-room', room);
script.setAttribute('data-user-id', user);

document.body.appendChild(script);
