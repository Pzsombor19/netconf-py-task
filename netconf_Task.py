from ncclient import manager
from ncclient.transport.errors import AuthenticationError, SSHError, SessionCloseError
from xml.dom import minidom
import getpass

#Futtatáshoz legalább Python 3.10+ szükséges, mivel használtam benne a match-case szerkezetet
#Tesztelés Dockerben történt, localhoston futó NETCONF szerverrel: 
# docker run -it --name netconf -p 830:830 --rm sysrepo/sysrepo-netopeer2:latest

def menu() -> str:
    print(
        "\nNETCONF MENÜ\n"
        "1) Aktuális NETCONF kapcsolat adatai\n"
        "2) Capabilities (támogatott funkciók)\n"
        "3) get-config (running)\n"
        "4) get (state + config) - teljes\n"
        "0) Kilépés\n"
    )
    return input("Válassz: ").strip()


def formOutput(xml_string: str) -> str:
    dom = minidom.parseString(xml_string) 
    return dom.toprettyxml(indent=" ")


def main():
    print("Kapcsolódás a NETCONF szerverhez")

    host = input("IP/host (127.0.0.1/localhost) [127.0.0.1]: ").strip() or "127.0.0.1"
    username = input("Felhasználónév (localhoston netconf) [netconf]: ").strip() or "netconf"
    password = getpass.getpass("Jelszó (localhoston netconf): ").strip() 
    port = 830

    try:
        print(f"\nKapcsolódás: {host}:{port}")
        with manager.connect(
            host=host,
            port=port,
            username=username,
            password=password,
            hostkey_verify=False,   
            allow_agent=False,
            look_for_keys=False,
            timeout=15,
            device_params={"name": "default"},
        ) as m:
            print("Sikeres csatlakozás!")

            while True:
                choice = menu()

                match choice:  
                    case "1":
                        print("\nAktuális NETCONF kapcsolat adatai:")
                        print(f"Session ID: {m.session_id}")
                        print(f"Kapcsolat aktív: {m.connected}")

                    case "2":
                        print("\nCapabilities (támogatott funkciók):")
                        for cap in m.server_capabilities:
                            print(f"- {cap}")

                    case "3":
                        print("\nget-config (running):")
                        reply = m.get_config(source="running")
                        print(formOutput(reply.xml))

                    case "4":
                        print("\nget (state + config):")
                        reply = m.get()
                        print(formOutput(reply.xml))

                    case "0":
                        print("Kilépés.")
                        break

                    case _:
                        print("Ismeretlen opció, válassz a menüből.")

    except AuthenticationError:
        print("Hitelesítési hiba: rossz felhasználónév/jelszó.")
    except (SSHError, SessionCloseError) as e:
        print(f"SSH/kapcsolódási hiba: {e}")
    except Exception as e:
        print(f"Hiba: {e}")


if __name__ == "__main__":
    main()
