def main():
    content = []
    with open("./models.py", "r") as file_in:
        content = file_in.readlines()

    new_content = []
    for line in content:
        clean_line = line.replace("\00", "")
        new_content.append(clean_line)

    with open("./myapp/models.py", "w", encoding="UTF-8") as file_out:
        for line in new_content:
            # print(line)
            file_out.write(line)


if __name__ == "__main__":
    main()
