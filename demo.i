dec greet(name) {
    give 'Hello, ' + name
}

name = ask('What is your name? ')

if name != '' {
    message = greet(name)
    yap(message)
} else {
    yap('You did not enter a name.')
}