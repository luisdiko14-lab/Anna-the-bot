function saveCommand() {
    const name = document.getElementById('cmdName').value;
    const response = document.getElementById('cmdResponse').value;
    const command = { name, response };
    
    let commands = JSON.parse(localStorage.getItem('custom_commands') || '[]');
    commands.push(command);
    localStorage.setItem('custom_commands', JSON.stringify(commands));
    
    document.getElementById('preview').innerText = `Saved: ${name}`;
    console.log("Command saved to localStorage", command);
}
