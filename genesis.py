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
    """Verifica si un comando está disponible en el PATH del sistema."""
    return shutil.which(command) is not None

def install_ipfs_linux():
    """Descarga e instala Kubo (IPFS) en distribuciones Linux."""
    print("\n[!] IPFS no detectado. Iniciando protocolo de instalación automática para Linux...")
    try:
        print(" [*] Descargando binarios de IPFS (Kubo)...")
        subprocess.run(["wget", "https://dist.ipfs.tech/kubo/v0.28.0/kubo_v0.28.0_linux-amd64.tar.gz"], check=True)
        
        print(" [*] Extrayendo paquete...")
        subprocess.run(["tar", "-xvzf", "kubo_v0.28.0_linux-amd64.tar.gz"], check=True)
        
        print(" [*] Moviendo ejecutable al sistema (Requiere contraseña sudo)...")
        subprocess.run(["sudo", "bash", "kubo/install.sh"], check=True)
        
        print(" [*] Limpiando archivos temporales...")
        subprocess.run(["rm", "-rf", "kubo", "kubo_v0.28.0_linux-amd64.tar.gz"])
        
        print("[+] IPFS instalado con éxito en el sistema.")
        return True
    except Exception as e:
        print(f"[-] Fallo crítico en la instalación de IPFS: {e}")
        print("[-] Deberás instalarlo manualmente: https://docs.ipfs.tech/install/command-line/")
        sys.exit(1)

def install_npm_linux():
    """Instala Node.js y npm usando el gestor de paquetes de Linux."""
    print("\n[!] NPM no detectado. Iniciando instalación de Node.js/npm...")
    try:
        # Detectar el gestor de paquetes (apt, pacman, dnf)
        if check_command("apt-get"):
            print(" [*] Sistema basado en Debian/Ubuntu detectado. Actualizando repositorios...")
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            print(" [*] Instalando npm...")
            subprocess.run(["sudo", "apt-get", "install", "-y", "npm"], check=True)
        elif check_command("pacman"):
            print(" [*] Sistema basado en Arch detectado. Instalando npm...")
            subprocess.run(["sudo", "pacman", "-S", "--noconfirm", "npm"], check=True)
        elif check_command("dnf"):
            print(" [*] Sistema basado en Fedora/RHEL detectado. Instalando npm...")
            subprocess.run(["sudo", "dnf", "install", "-y", "npm"], check=True)
        else:
            print("[-] Gestor de paquetes no soportado para instalación automática.")
            print("[-] Por favor instala Node.js/npm manualmente.")
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
            print("[-] En Windows o macOS debes instalarlo manualmente.")
            sys.exit(1)
    
    # Inicializa el repo si no existe
    subprocess.run(["ipfs", "init"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Habilitar PubSub
    print("[+] Habilitando protocolo PubSub...")
    subprocess.run(["ipfs", "config", "--json", "Pubsub.Enabled", "true"])
    
    print("[+] Levantando demonio IPFS...")
    if os.name == 'nt':  # Windows
        subprocess.Popen(["start", "cmd", "/k", "ipfs daemon --enable-pubsub-experiment"], shell=True)
    else:  # Mac/Linux
        try:
            subprocess.Popen(["x-terminal-emulator", "-e", "ipfs daemon --enable-pubsub-experiment"])
        except FileNotFoundError:
            subprocess.Popen("ipfs daemon --enable-pubsub-experiment > /dev/null 2>&1 &", shell=True)
    
    print("[+] Nodo IPFS operativo en segundo plano. Escuchando el enjambre.")

def install_admin_panel():
    print("\n[+] INICIANDO BÚNKER DE MANDO (NODO + FLASK + WEB)...")
    
    # 0. Verificar e instalar dependencias (npm) en Linux
    if not check_command("npm"):
        if platform.system() == "Linux":
            install_npm_linux()
        else:
            print("[-] ERROR: npm no está instalado en el sistema.")
            print("[-] Debes instalar Node.js manualmente para continuar.")
            sys.exit(1)

    # 1. Levantar el nodo IPFS
    init_ipfs_node_only()
    time.sleep(3) 
    
    # 2. Levantar el Backend (Flask)
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

    # 3. Preparar e iniciar el Frontend (Vite)
    print("[+] Levantando servidor web local...")
    frontend_path = os.path.join(os.getcwd(), "red-omega-front")
    if not os.path.exists(frontend_path):
        frontend_path = os.path.join(os.getcwd(), "frontend")
    
    try:
        if os.name == 'nt':
            # Verificamos si node_modules existe, si no, corremos npm install primero
            if not os.path.exists(os.path.join(frontend_path, "node_modules")):
                print(" [*] Instalando dependencias de Vue (esto tomará un momento)...")
                subprocess.run(["cmd", "/c", f"cd {frontend_path} && npm install"], check=True)
            subprocess.Popen(["start", "cmd", "/c", f"cd {frontend_path} && npm run dev"], shell=True)
        else:
            if not os.path.exists(os.path.join(frontend_path, "node_modules")):
                print(" [*] Instalando dependencias de Vue (esto tomará un momento)...")
                subprocess.run(["bash", "-c", f"cd {frontend_path} && npm install"], check=True)
            try:
                subprocess.Popen(["x-terminal-emulator", "-e", f"bash -c 'cd {frontend_path} && npm run dev'"])
            except FileNotFoundError:
                subprocess.Popen(f"cd {frontend_path} && npm run dev &", shell=True)
        
        # Esperar a que Vite compile y abrir el navegador nativo
        print("[+] Abriendo interfaz en el navegador...")
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