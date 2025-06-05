async function cadastrar(e) {
  e.preventDefault();

  const email = document.getElementById('email').value.trim();
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    alert('E-mail inválido!');
    return;
  }

  if (!username || !password) {
    alert('Preencha todos os campos obrigatórios!');
    return;
  }

  const data = {
    "email": email,
    "username": username,
    "password": password
  }

  const res = await fetch('http://localhost:3000/cadastrar', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) alert('Usuário cadastrado!');
    else alert(data.message);
  })
  .catch(err => alert('Erro ao cadastrar.'));

  console.log(res);
}
