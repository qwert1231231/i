yap('=== I Language File I/O Example ===')

yap('Writing to file...')
write('output.txt', 'Hello from I!\nThis is line 2.\n')
yap('File written!')

yap('Reading from file...')
content = read('output.txt')
yap('File contents:')
yap(content)

yap('Appending to file...')
append('output.txt', 'This is appended!\n')
yap('Content appended!')

yap('Updated file contents:')
new_content = read('output.txt')
yap(new_content)

yap('=== Done! ===')

