async function cadastrar(e) {
  e.preventDefault();

  const email = document.getElementById('email').value.trim();
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;

  const data = {
    "email": email,
    "username": username,
    "password": password
  }

  const res = await fetch('https://xdes-04-stop-73agu5whg-rodrigoruans-projects.vercel.app/cadastrar', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      alert("Usuário cadastrado com sucesso.");
      window.location.href = './login.html';
    } else {
      alert(data.message);
    }
  })
  .catch(err => alert('Erro ao cadastrar.'));

  console.log(res);
}

async function entrar(e) {
  e.preventDefault();

  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;

  const data = {
    "email": email,
    "password": password
  }

  const res = await fetch('https://xdes-04-stop-73agu5whg-rodrigoruans-projects.vercel.app/logar', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      alert("Logado com sucesso.");
      window.location.href = './homepage.html';
    } else {
      alert(data.message);
    }
  })
  .catch(err => alert(err));

  console.log(res);
}
