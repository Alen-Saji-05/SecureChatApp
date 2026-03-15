# SecureChatApp

A secure, multi-client chat application built with Python. It features a centralized server for message broadcasting and encrypted communication using RSA for key exchange and AES for message encryption. The client includes a graphical user interface (GUI) built with Tkinter.

## Features

*   **Multi-client Chat:** Connect multiple clients to a central server to chat in a shared room.
*   **Encrypted Communication:**
    *   **RSA Key Exchange:** Uses 2048-bit RSA for secure exchange of the symmetric session key.
    *   **AES Encryption:** Messages are encrypted using AES in CFB mode.
    *   **Message Integrity:** Ensures messages are not tampered with during transmission using HMAC-SHA256.
*   **Graphical User Interface:** Easy-to-use GUI built with Python's built-in `tkinter` library.

## Requirements

*   Python 3.x
*   `cryptography` library

You can install the required dependency using pip:

```bash
pip install cryptography
```

## How to Run

1.  **Start the Server:**
    Open a terminal and run the server script:
    ```bash
    python Server.py
    ```
    The server will start listening on `127.0.0.1:5000`.

2.  **Start the Clients:**
    Open another terminal (or multiple terminals for multiple clients) and run the client script:
    ```bash
    python gui_client.py
    ```
    This will open the chat window.

3.  **Chat:**
    Wait for the AES key to be established (you will see a system message indicating "Secure AES key established" or "Waiting for a peer to secure the connection..."). Once a secure connection is established between clients, you can start sending messages securely.

## Files

*   `Server.py`: The server script responsible for accepting connections and broadcasting encrypted messages to all connected clients. It does not read or decrypt the messages.
*   `gui_client.py`: The client script that handles the user interface and all cryptographic operations for secure communication.
