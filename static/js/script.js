// Atalho para envio com a tecla Enter
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('input[type="text"]').forEach(input => {
    input.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        if(this.id.startsWith("msg-")){
          let ia = this.id.split("-")[1];
          enviarMensagem(ia);
        } else if(this.id === "msg-reuniao"){
          enviarReuniao();
        }
      }
    });
  });
});

function enviarMensagem(ia) {
  let inputId = "msg-" + ia;
  let msg = document.getElementById(inputId).value;
  let chatBox = document.getElementById("chat-" + ia);
  fetch("/enviar", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ ia: ia, mensagem: msg })
  })
  .then(response => response.json())
  .then(data => {
    chatBox.innerHTML += `<div><strong>Você:</strong> ${msg}</div>`;
    chatBox.innerHTML += `<div><strong>${ia}:</strong> ${data.resposta}</div>`;
    document.getElementById(inputId).value = "";
    chatBox.scrollTop = chatBox.scrollHeight;
  });
}

function treinarDeep() {
  let treinarMsg = document.getElementById("treinar-msg").value;
  let ia = document.getElementById("treinar-ia").value;
  fetch("/treinar_deepseek", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ ia: ia, mensagem: treinarMsg })
  })
  .then(response => response.json())
  .then(data => {
    alert(data.resultado);
    document.getElementById("treinar-msg").value = "";
  });
}

function enviarReuniao() {
  let msg = document.getElementById("msg-reuniao").value;
  let chatBox = document.getElementById("chat-reuniao");
  let ias = ["z4quel", "l3ticia", "symbio"];
  chatBox.innerHTML += `<div><strong>Você (Reunião):</strong> ${msg}</div>`;
  ias.forEach(ia => {
    fetch("/enviar", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ ia: ia, mensagem: msg })
    })
    .then(response => response.json())
    .then(data => {
      chatBox.innerHTML += `<div><strong>${ia}:</strong> ${data.resposta}</div>`;
      chatBox.scrollTop = chatBox.scrollHeight;
    });
  });
  document.getElementById("msg-reuniao").value = "";
}

function atualizarMonitoramento() {
  fetch("/api/monitoramento")
  .then(response => response.json())
  .then(data => {
    document.getElementById("monitoramento-texto").innerHTML =
      `<p>Total mensagens: ${data.total_mensagens}</p>
       <p>Última atualização: ${data.ultima_atualizacao}</p>
       <p>Níveis de autonomia: Z4quel: ${data.niveis.z4quel}, L3ticia: ${data.niveis.l3ticia}, Symbio: ${data.niveis.symbio}</p>`;
       
    let ctx = document.getElementById('grafico-monitoramento').getContext('2d');
    if(window.monitorChart) {
      window.monitorChart.data.datasets[0].data = [data.total_mensagens];
      window.monitorChart.update();
    } else {
      window.monitorChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Total Mensagens'],
          datasets: [{
            label: 'Mensagens recebidas',
            data: [data.total_mensagens],
            backgroundColor: ['#3B82F6']
          }]
        },
        options: {
          scales: {
            y: { beginAtZero: true }
          }
        }
      });
    }
  });
}
setInterval(atualizarMonitoramento, 10000);
atualizarMonitoramento();