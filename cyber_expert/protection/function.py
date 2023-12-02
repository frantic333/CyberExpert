def tool_file_size(instance, file):
    if file.size <= 104857600:
        return file
