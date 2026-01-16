const scriptTag = document.currentScript;

const data = scriptTag.dataset

// console.log("params->> ", data.websiteName)

const server_url = data.serverUrl
const website_name = data.websiteName
////////////////////////////////////////////////////////////

// LIVEKIT

////////////////////////////////////////////////////////////


function randomId(prefix = "", len = 6) {
    return (
        prefix +
        Math.random().toString(36).substring(2, 2 + len)
    );
}

// const room = randomId("room-");
const user = randomId("user-");

const script = document.createElement("script");
script.src = `${server_url}/embed-popup.js`;

script.setAttribute('data-lk-sandbox-id', server_url);
script.setAttribute('data-room', user);
script.setAttribute('data-user-id', user);
script.setAttribute('data-website-name', website_name);

document.body.appendChild(script);





////////////////////////////////////////////////////////////

// SOCKET

////////////////////////////////////////////////////////////
const socketScript = document.createElement('script');
socketScript.src = "https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js";
socketScript.integrity = "sha512-q/dWJ3kcmjBLU4Qc47E4A9kTB4m3wuTY7vkFJDTZKjTs8jhyGQnaUrxa0Ytd0ssMZhbNua9hE+E7Qv1j+DyZwA==";
socketScript.crossOrigin = "anonymous";
socketScript.referrerPolicy = "no-referrer";
// wait for the script to load before using `io`
socketScript.addEventListener('load', () => {

    const socket = io('http://127.0.0.1:5000',{
        query: {
            user_id: user,
            website_name: website_name
        }
    });
    socket.on('connect', function() {
        console.log("CONNECTED !");
    });

    // EVENTS
    socket.on('click', function(data) {
        const { xpath } = data;
        console.log(`clicking on ${xpath}`);

        // Find element by XPath
        const element = document.evaluate(
            xpath,
            document,
            null,
            XPathResult.FIRST_ORDERED_NODE_TYPE,
            null
        ).singleNodeValue;

        if (element) {
            element.click(); // perform click
            console.log('Clicked successfully!');
        } else {
            console.log('Element not found');
        }
    });

    socket.on('send-input', function(data) {
        const { xpath, value } = data;
        console.log(`sending input to ${xpath}`, value);

        // Find element by XPath
        const element = document.evaluate(
            xpath,
            document,
            null,
            XPathResult.FIRST_ORDERED_NODE_TYPE,
            null
        ).singleNodeValue;

        if (!element) {
            console.log('Element not found');
            return;
        }

        // Focus element
        try { element.focus(); } catch (e) {}

        // If it's an input/textarea/select
        const tag = element.tagName && element.tagName.toLowerCase();
        if (tag === 'input' || tag === 'textarea' || tag === 'select') {
            element.value = value ?? '';
            // move caret to end
            if (typeof element.setSelectionRange === 'function') {
                const len = element.value.length;
                element.setSelectionRange(len, len);
            }
            // Dispatch input/change events so listeners react
            element.dispatchEvent(new Event('input', { bubbles: true }));
            element.dispatchEvent(new Event('change', { bubbles: true }));
            console.log('Value set on form control');
            return;
        }

        // If contenteditable
        if (element.isContentEditable) {
            element.innerText = value ?? '';
            element.dispatchEvent(new Event('input', { bubbles: true }));
            console.log('Value set on contenteditable');
            return;
        }

        // Fallback: set innerText
        element.innerText = value ?? '';
        console.log('Value set on element.innerText');
    });

});

socketScript.addEventListener('error', (e) => {
    console.error('Failed to load socket.io client', e);
});

document.head.appendChild(socketScript);

