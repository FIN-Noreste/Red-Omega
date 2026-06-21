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

def install_ipfs_linux():
    """Descarga e instala Kubo (IPFS) en distribuciones Linux."""
    print("\n[!] IPFS no detectado. Iniciando protocolo de instalación automática para Linux...")
    try:
        # Descargar la última versión estable (Kubo)
        print(" [*] Descargando binarios de IPFS (Kubo)...")
        subprocess.run(["wget", "https://dist.ipfs.tech/kubo/v0.28.0/kubo_v0.28.0_linux-amd64.tar.gz"], check=True)
        
        # Extraer
        print(" [*] Extrayendo paquete...")
        subprocess.run(["tar", "-xvzf", "kubo_v0.28.0_linux-amd64.tar.gz"], check=True)
        
        # Instalar (Requiere permisos de administrador para mover a /usr/local/bin)
        print(" [*] Moviendo ejecutable al sistema (Requiere contraseña sudo)...")
        subprocess.run(["sudo", "bash", "kubo/install.sh"], check=True)
        
        # Limpiar basura
        print(" [*] Limpiando archivos temporales...")
        subprocess.run(["rm", "-rf", "kubo", "kubo_v0.28.0_linux-amd64.tar.gz"])
        
        print("[+] IPFS instalado con éxito en el sistema.")
        return True
    except Exception as e:
        print(f"[-] Fallo crítico en la instalación de IPFS: {e}")
        print("[-] Deberás instalarlo manualmente: https://docs.ipfs.tech/install/command-line/")
        sys.exit(1)

def init_ipfs_node_only():
    print("\n[+] INICIANDO PUNTO OMEGA (MODO NODO SILENCIOSO)...")
    
    if not check_ipfs():
        if platform.system() == "Linux":
            install_ipfs_linux()
        else:
            print("[-] ERROR: Kubo IPFS no está instalado o no está en el PATH.")
            print("[-] En Windows o macOS debes instalarlo manualmente.")
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
    print("\n[+] INICIANDO BÚNKER DE MANDO (NODO + FLASK + WEB)...")
    
    # 1. Levantar el nodo IPFS
    init_ipfs_node_only()
    time.sleep(3) # Dar tiempo a que el nodo respire
    
    # 2. Levantar el Backend (Flask)
    print("[+] Iniciando Motor Flask Local...")
    backend_path = os.path.join(os.getcwd(), "backend", "app.py")
    # Alternativa por si el folder se llama diferente
    if not os.path.exists(backend_path):
        backend_path = os.path.join(os.getcwd(), "bunker", "backend", "app.py")

    if os.name == 'nt':
        subprocess.Popen(["start", "cmd", "/k", f"python {backend_path}"], shell=True)
    else:
        subprocess.Popen(["x-terminal-emulator", "-e", f"python3 {backend_path}"])

    # 3. Levantar el Frontend en el Navegador
    print("[+] Levantando servidor web local...")
    frontend_path = os.path.join(os.getcwd(), "red-omega-front")
    if not os.path.exists(frontend_path):
        frontend_path = os.path.join(os.getcwd(), "frontend")
    
    try:
        if os.name == 'nt':
            subprocess.Popen(["start", "cmd", "/c", f"cd {frontend_path} && npm run dev"], shell=True)
        else:
            subprocess.Popen(["x-terminal-emulator", "-e", f"bash -c 'cd {frontend_path} && npm run dev'"])
        
        # Esperar a que Vite compile y abrir el navegador nativo
        print("[+] Abriendo interfaz en el navegador...")
        time.sleep(3)
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