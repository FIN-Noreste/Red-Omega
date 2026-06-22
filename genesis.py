import os
import sys
import platform
import subprocess
import time
import webbrowser
import shutil

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print("""
    ██████╗ ███████╗██████╗     ██████╗ ███╗   ███╗███████╗ ██████╗  █████╗ 
    ██╔══██╗██╔════╝██╔══██╗   ██╔═══██╗████╗ ████║██╔════╝██╔════╝ ██╔══██╗
    ██████╔╝█████╗  ██║  ██║   ██║   ██║██╔████╔██║█████╗  ██║  ███╗███████║
    ██╔══██╗██╔══╝  ██║  ██║   ██║   ██║██║╚██╔╝██║██╔══╝  ██║   ██║██╔══██║
    ██║  ██║███████╗██████╔╝   ╚██████╔╝██║ ╚═╝ ██║███████╗╚██████╔╝██║  ██║
    ╚═╝  ╚═╝╚══════╝╚═════╝     ╚═════╝ ╚═╝     ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝
    """)
    print("    [ INICIALIZADOR DE RED P2P ] OS Detectado:", platform.system())
    print("    ==============================================================\n")

def check_command(command):
    return shutil.which(command) is not None

def install_ipfs_linux():
    print("\n[!] IPFS no detectado. Iniciando protocolo de instalación automática para Linux...")
    try:
        subprocess.run(["wget", "https://dist.ipfs.tech/kubo/v0.28.0/kubo_v0.28.0_linux-amd64.tar.gz"], check=True)
        subprocess.run(["tar", "-xvzf", "kubo_v0.28.0_linux-amd64.tar.gz"], check=True)
        subprocess.run(["sudo", "bash", "kubo/install.sh"], check=True)
        subprocess.run(["rm", "-rf", "kubo", "kubo_v0.28.0_linux-amd64.tar.gz"])
        print("[+] IPFS instalado con éxito en el sistema.")
        return True
    except Exception as e:
        print(f"[-] Fallo crítico en la instalación de IPFS: {e}")
        sys.exit(1)

def install_npm_linux():
    print("\n[!] NPM no detectado. Iniciando instalación de Node.js/npm...")
    try:
        if check_command("apt-get"):
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", "npm"], check=True)
        elif check_command("pacman"):
            subprocess.run(["sudo", "pacman", "-S", "--noconfirm", "npm"], check=True)
        elif check_command("dnf"):
            subprocess.run(["sudo", "dnf", "install", "-y", "npm"], check=True)
        else:
            print("[-] Gestor de paquetes no soportado para instalación automática.")
            sys.exit(1)
        print("[+] NPM instalado con éxito.")
        return True
    except Exception as e:
        print(f"[-] Error instalando npm: {e}")
        sys.exit(1)

def init_ipfs_node_only():
    print("\n[+] INICIANDO PUNTO OMEGA (MODO NODO SILENCIOSO)...")
    
    if not check_command("ipfs"):
        if platform.system() == "Linux":
            install_ipfs_linux()
        else:
            print("[-] ERROR: Kubo IPFS no está instalado o no está en el PATH.")
            sys.exit(1)
    
    subprocess.run(["ipfs", "init"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # === INYECCIÓN DEL NODO FARO (BOOTSTRAP & RELAY) ===
    print("[+] Limpiando enrutamiento corporativo y configurando Nodo Faro de la Red Omega...")
    
    # 1. Purgar nodos públicos de Protocol Labs
    subprocess.run(["ipfs", "bootstrap", "rm", "--all"], stdout=subprocess.DEVNULL)
    
    # 2. Inyectar tu Faro de Google Cloud (TCP)
    faro_address = "/ip4/34.31.146.218/tcp/4001/p2p/12D3KooWHdxx9nAoseYop65QYZbFDVrHztKK5otMNVtc4LkMmr55"
    subprocess.run(["ipfs", "bootstrap", "add", faro_address], stdout=subprocess.DEVNULL)

    # 3. Forzar el uso del Faro como Relay (para atravesar Firewalls)
    relay_address = "/ip4/34.31.146.218/tcp/4001/p2p/12D3KooWHdxx9nAoseYop65QYZbFDVrHztKK5otMNVtc4LkMmr55/p2p-circuit"
    subprocess.run(["ipfs", "swarm", "peering", "add", relay_address], stdout=subprocess.DEVNULL)
    # === FIN DE INYECCIÓN DEL FARO ===

    print("[+] Configurando Perforación de NAT y PubSub...")
    subprocess.run(["ipfs", "config", "--json", "Pubsub.Enabled", "true"], stdout=subprocess.DEVNULL)
    subprocess.run(["ipfs", "config", "--json", "Swarm.EnableHolePunching", "true"], stdout=subprocess.DEVNULL)
    subprocess.run(["ipfs", "config", "--json", "Swarm.RelayClient.Enabled", "true"], stdout=subprocess.DEVNULL)
    subprocess.run(["ipfs", "config", "Routing.Type", "dht"], stdout=subprocess.DEVNULL)
    
    # === REPARACIÓN DE CORS PARA EL GATEWAY LOCAL ===
    print("[+] Inyectando permisos de acceso cruzado (CORS)...")
    subprocess.run(["ipfs", "config", "--json", "API.HTTPHeaders.Access-Control-Allow-Origin", "[\"*\"]"], stdout=subprocess.DEVNULL)
    subprocess.run(["ipfs", "config", "--json", "API.HTTPHeaders.Access-Control-Allow-Methods", "[\"PUT\", \"GET\", \"POST\", \"OPTIONS\"]"], stdout=subprocess.DEVNULL)
    
    subprocess.run(["ipfs", "config", "--json", "Gateway.HTTPHeaders.Access-Control-Allow-Origin", "[\"*\"]"], stdout=subprocess.DEVNULL)
    subprocess.run(["ipfs", "config", "--json", "Gateway.HTTPHeaders.Access-Control-Allow-Methods", "[\"PUT\", \"GET\", \"POST\", \"OPTIONS\"]"], stdout=subprocess.DEVNULL)
    subprocess.run(["ipfs", "config", "--json", "Gateway.HTTPHeaders.Access-Control-Allow-Headers", "[\"Authorization\", \"Content-Type\"]"], stdout=subprocess.DEVNULL)
    # === FIN DE REPARACIÓN DE CORS ===

    print("[+] Levantando demonio IPFS...")
    if os.name == 'nt':
        subprocess.Popen(["start", "cmd", "/k", "ipfs daemon"], shell=True)
    else:
        try:
            subprocess.Popen(["x-terminal-emulator", "-e", "ipfs daemon"])
        except FileNotFoundError:
            subprocess.Popen("ipfs daemon > /dev/null 2>&1 &", shell=True)
    
    print("[+] Nodo IPFS anclado al Faro. Escuchando a la Red Omega.")

def install_admin_panel():
    print("\n[+] INICIANDO BÚNKER DE MANDO (NODO + FLASK + WEB)...")
    
    if not check_command("npm"):
        if platform.system() == "Linux":
            install_npm_linux()
        else:
            print("[-] ERROR: npm no está instalado en el sistema.")
            sys.exit(1)

    init_ipfs_node_only()
    time.sleep(3) 
    
    print("[+] Iniciando Motor Flask Local...")
    backend_path = os.path.join(os.getcwd(), "backend", "app.py")
    if not os.path.exists(backend_path):
        backend_path = os.path.join(os.getcwd(), "bunker", "backend", "app.py")

    if os.name == 'nt':
        subprocess.Popen(["start", "cmd", "/k", f"python {backend_path}"], shell=True)
    else:
        try:
            subprocess.Popen(["x-terminal-emulator", "-e", f"python3 {backend_path}"])
        except FileNotFoundError:
            subprocess.Popen(f"python3 {backend_path} &", shell=True)

    print("[+] Levantando servidor web local...")
    frontend_path = os.path.join(os.getcwd(), "red-omega-front")
    if not os.path.exists(frontend_path):
        frontend_path = os.path.join(os.getcwd(), "frontend")
    
    try:
        if os.name == 'nt':
            if not os.path.exists(os.path.join(frontend_path, "node_modules")):
                subprocess.run(["cmd", "/c", f"cd {frontend_path} && npm install"], check=True)
            subprocess.Popen(["start", "cmd", "/c", f"cd {frontend_path} && npm run dev"], shell=True)
        else:
            if not os.path.exists(os.path.join(frontend_path, "node_modules")):
                subprocess.run(["bash", "-c", f"cd {frontend_path} && npm install"], check=True)
            try:
                subprocess.Popen(["x-terminal-emulator", "-e", f"bash -c 'cd {frontend_path} && npm run dev'"])
            except FileNotFoundError:
                subprocess.Popen(f"cd {frontend_path} && npm run dev &", shell=True)
        
        time.sleep(4)
        webbrowser.open("http://localhost:5173")
        print("[+] Búnker completamente operativo.")
    except Exception as e:
        print(f"[-] Error al iniciar el frontend: {e}")

def main():
    clear_screen()
    print_banner()
    print("  1. Iniciar Punto Omega (Solo Nodo IPFS)")
    print("  2. Iniciar Búnker de Mando (Nodo IPFS + Flask + Navegador)")
    print("  3. Salir")
    print("    ==============================================================")
    
    opcion = input("\n  > Selecciona un protocolo [1-3]: ")
    if opcion == '1': init_ipfs_node_only()
    elif opcion == '2': install_admin_panel()
    elif opcion == '3': sys.exit(0)
    else: main()

if __name__ == "__main__":
    main()