// Página de Rafael Kingeski: abas e a linha "Agora" do horário.
document.documentElement.classList.add("js");

// ---------- abas (o endereço #horario abre direto a aba do horário) ----------
const abas = [...document.querySelectorAll(".abas a")];
const paineis = [...document.querySelectorAll(".painel")];
function mostrarAba(nome){
  if(!paineis.some(p => p.dataset.painel === nome)) nome = "inicio";  // aba principal (o antigo #sobre também cai aqui)
  paineis.forEach(p => { p.hidden = p.dataset.painel !== nome; });
  abas.forEach(a => {
    if(a.dataset.aba === nome) a.setAttribute("aria-current", "page");
    else a.removeAttribute("aria-current");
  });
}
abas.forEach(a => a.addEventListener("click", event => {
  event.preventDefault();
  history.replaceState(null, "", `#${a.dataset.aba}`);
  mostrarAba(a.dataset.aba);
}));
window.addEventListener("hashchange", () => mostrarAba(location.hash.slice(1)));
mostrarAba(location.hash.slice(1));

// ---------- "Agora": lê o horário pela hora de Brasília ----------
const DIAS = ["domingo", "segunda", "terça", "quarta", "quinta", "sexta", "sábado"];
const minutos = hhmm => { const [h, m] = hhmm.split(":").map(Number); return h * 60 + m; };
function agoraEmBrasilia(){
  const partes = Object.fromEntries(new Intl.DateTimeFormat("en-US", {timeZone: "America/Sao_Paulo", weekday: "short", hour: "2-digit", minute: "2-digit", hourCycle: "h23"})
    .formatToParts(new Date()).map(p => [p.type, p.value]));
  return {dia: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].indexOf(partes.weekday), min: Number(partes.hour) * 60 + Number(partes.minute)};
}
function descrever(slot){
  const sala = slot.querySelector("span")?.textContent;
  if(slot.classList.contains("aula")) return `em aula de ${slot.title}${sala ? ` na sala ${sala}` : ""}`;
  if(slot.classList.contains("atendimento")) return "em atendimento ao aluno";
  if(slot.classList.contains("pesquisa")) return `em pesquisa${sala ? ` na sala ${sala}` : ""}`;
  return `no ${slot.title}`;
}
function atualizarAgora(){
  const slots = [...document.querySelectorAll(".semana .slot")];
  const {dia, min} = agoraEmBrasilia();
  slots.forEach(s => s.classList.remove("agora-slot"));
  const atual = slots.find(s => Number(s.dataset.dia) === dia && min >= minutos(s.dataset.ini) && min < minutos(s.dataset.fim));
  if(atual) atual.classList.add("agora-slot");
  // próximo atendimento: o mais cedo a partir de agora, dando a volta na semana
  const proximo = slots.filter(s => s.classList.contains("atendimento"))
    .map(s => {
      let falta = ((Number(s.dataset.dia) - dia + 7) % 7) * 1440 + minutos(s.dataset.ini) - min;
      if(falta + minutos(s.dataset.fim) - minutos(s.dataset.ini) <= 0) falta += 7 * 1440;
      return {s, falta};
    })
    .sort((a, b) => a.falta - b.falta)[0];
  let quando = "a combinar";
  if(proximo){
    const d = Number(proximo.s.dataset.dia);
    quando = proximo.falta <= 0 ? "agora" : `${d === dia && proximo.falta < 1440 ? "hoje" : d === (dia + 1) % 7 && proximo.falta < 2880 ? "amanhã" : DIAS[d]} às ${proximo.s.dataset.ini}`;
  }
  const hora = `${Math.floor(min / 60)}h${String(min % 60).padStart(2, "0")}`;
  const estado = atual ? descrever(atual) : "fora do horário de aulas";
  document.getElementById("agora").innerHTML = `<span class="pulso" aria-hidden="true"></span><b>Agora</b> (${DIAS[dia]}, ${hora}): ${estado}. Próximo atendimento: ${quando}.`;
}
atualizarAgora();
setInterval(atualizarAgora, 60 * 1000);
