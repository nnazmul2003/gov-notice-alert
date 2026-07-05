def check_sites():
    last = load_last()
    updated = False

    print("===== START CHECK =====")

    for name, url in SITES.items():

        print(f"Checking site: {name}")
        print(f"URL: {url}")

        try:
            notice = get_latest_notice(url)

            print("Notice:", notice)

            if not notice:
                print("No notice found.")
                continue

            title = f"TEST - {name.upper()} Notice"
            body = f"{notice['title']}\n\n{notice['link']}"

            print("Sending ntfy...")
            send_ntfy(title, body)

            print("Sending email...")
            send_email(title, body)

            print("Test notification sent.")

            if notice["link"] != last.get(name, ""):
                last[name] = notice["link"]
                updated = True

        except Exception as e:
            print(f"ERROR ({name}):", e)

    if updated:
        save_last(last)

    print("===== END CHECK =====")
