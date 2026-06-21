import os
import sys
import platform
import subprocess
import time
import webbrowser

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

def check_ipfs():
    """Verifica si IPFS está instalado en el sistema."""
    try:
        subprocess.run(["ipfs", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except FileNotFoundError:
        return False

def init_ipfs_node_only():
    print("\n[+] INICIANDO PUNTO OMEGA (MODO NODO SILENCIOSO)...")
    if not check_ipfs():
        print("[-] ERROR: Kubo IPFS no está instalado o no está en el PATH.")
        sys.exit(1)
    
    # Inicializa el repo si no existe
    subprocess.run(["ipfs", "init"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Habilitar PubSub (El sistema nervioso)
    print("[+] Habilitando protocolo PubSub...")
    subprocess.run(["ipfs", "config", "--json", "Pubsub.Enabled", "true"])
    
    print("[+] Levantando demonio IPFS...")
    # Corre el demonio en una ventana separada dependiendo del OS
    if os.name == 'nt':  # Windows
        subprocess.Popen(["start", "cmd", "/k", "ipfs daemon --enable-pubsub-experiment"], shell=True)
    else:  # Mac/Linux
        subprocess.Popen(["x-terminal-emulator", "-e", "ipfs daemon --enable-pubsub-experiment"])
    
    print("[+] Nodo IPFS operativo en segundo plano. Escuchando el enjambre.")

def install_admin_panel():
    print("\n[+] INICIANDO BÚNKER WEB (NODO + FLASK + VUE)...")
    
    # 1. Levantar el nodo IPFS
    init_ipfs_node_only()
    time.sleep(3) # Dar tiempo a que el nodo respire
    
    # 2. Levantar el Backend (Flask)
    print("[+] Iniciando Motor Flask Local...")
    backend_path = os.path.join(os.getcwd(), "backend", "app.py")
    if os.name == 'nt':
        subprocess.Popen(["start", "cmd", "/k", f"python {backend_path}"], shell=True)
    else:
        subprocess.Popen(["x-terminal-emulator", "-e", f"python3 {backend_path}"])

    # 3. Levantar el Frontend en el navegador (Vite)
    print("[+] Compilando interfaz web (Vue/Vite)...")
    frontend_path = os.path.join(os.getcwd(), "red-omega-front")
    
    try:
        if os.name == 'nt':
            # Usa 'npm run dev' en lugar de 'npm run electron:dev'
            subprocess.Popen(["start", "cmd", "/k", f"cd {frontend_path} && npm run dev"], shell=True)
        else:
            subprocess.Popen(["x-terminal-emulator", "-e", f"bash -c 'cd {frontend_path} && npm run dev'"])
        
        # Le damos un par de segundos a Vite para compilar, y abrimos el navegador
        time.sleep(3)
        webbrowser.open('http://localhost:5173')
        print("[+] Búnker levantado en tu navegador web.")
        
    except Exception as e:
        print(f"[-] Error al iniciar el frontend: {e}")

def main():
    clear_screen()
    print_banner()
    print("  1. Iniciar Punto Omega (Solo Nodo IPFS)")
    print("  2. Iniciar Búnker de Mando (Nodo + Motor Backend + Panel Web)")
    print("  3. Salir")
    print("    ==============================================================")
    
    opcion = input("\n  > Selecciona un protocolo [1-3]: ")
    
    if opcion == '1':
        init_ipfs_node_only()
    elif opcion == '2':
        install_admin_panel()
    elif opcion == '3':
        print("[+] Abortando secuencia.")
        sys.exit(0)
    else:
        print("[-] Opción no válida.")
        time.sleep(1)
        main()

if __name__ == "__main__":
    main()