import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import os

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

HOST = "127.0.0.1"
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# RSA keys
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

public_key = private_key.public_key()

public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

aes_key = None

# Send our public key to any already connected clients or future ones
client.send(public_pem)

def encrypt_message(msg):
    iv = os.urandom(16)

    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
    encryptor = cipher.encryptor()

    ciphertext = encryptor.update(msg) + encryptor.finalize()

    h = hmac.HMAC(aes_key, hashes.SHA256())
    h.update(iv + ciphertext)
    mac = h.finalize()

    return iv + mac + ciphertext


def decrypt_message(data):
    iv = data[:16]
    mac = data[16:48]
    ciphertext = data[48:]

    h = hmac.HMAC(aes_key, hashes.SHA256())
    h.update(iv + ciphertext)
    try:
        h.verify(mac)
    except:
        return "Integrity check failed"

    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
    decryptor = cipher.decryptor()

    msg = decryptor.update(ciphertext) + decryptor.finalize()
    return msg.decode()


def receive():
    global aes_key
    while True:
        try:
            data = client.recv(4096)
            if not data:
                break

            if data.startswith(b"-----BEGIN PUBLIC KEY-----"):
                peer_public_key = serialization.load_pem_public_key(data)
                
                # Use deterministic AES key generation
                if aes_key is None:
                    aes_key = os.urandom(32)
                
                # Send encrypted AES key back to the peer
                encrypted_key = peer_public_key.encrypt(
                    aes_key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                client.send(encrypted_key)
                continue

            if len(data) == 256:
                try:
                    decrypted_key = private_key.decrypt(
                        data,
                        padding.OAEP(
                            mgf=padding.MGF1(algorithm=hashes.SHA256()),
                            algorithm=hashes.SHA256(),
                            label=None
                        )
                    )
                    # Use deterministic key resolution if connection happens concurrently
                    if aes_key is None or decrypted_key > aes_key:
                        aes_key = decrypted_key
                        chat.insert(tk.END, "System: Secure AES key established.\n")
                        chat.see(tk.END)
                    continue
                except Exception:
                    # In case of 256 byte ciphertext collision, let it fallback to AES decryption
                    pass

            if aes_key is not None:
                msg = decrypt_message(data)
                if msg != "Integrity check failed":
                    chat.insert(tk.END, "Peer: " + msg + "\n")
                else:
                    chat.insert(tk.END, "System: Received invalid/corrupted message.\n")
                chat.see(tk.END)

        except Exception as e:
            chat.insert(tk.END, f"System Error: {e}\n")
            chat.see(tk.END)
            break


def send():
    msg = entry.get()
    
    if msg == "":
        return
        
    if aes_key is None:
        chat.insert(tk.END, "System: Waiting for a peer to secure the connection...\n")
        chat.see(tk.END)
        return

    try:
        encrypted = encrypt_message(msg.encode())
        client.send(encrypted)
        chat.insert(tk.END, "You: " + msg + "\n")
        chat.see(tk.END)
        entry.delete(0, tk.END)
    except Exception as e:
        chat.insert(tk.END, f"System: Failed to send message. {e}\n")
        chat.see(tk.END)


window = tk.Tk()
window.title("Secure Encrypted Chat")

chat = scrolledtext.ScrolledText(window, width=60, height=20)
chat.pack(pady=10, padx=10)

entry = tk.Entry(window, width=50)
entry.pack(side=tk.LEFT, padx=10, pady=10)

btn = tk.Button(window, text="Send", command=send)
btn.pack(side=tk.LEFT, pady=10)

threading.Thread(target=receive, daemon=True).start()

window.mainloop()