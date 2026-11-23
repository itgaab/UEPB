/* UEPB Orienta: interface do site. A lógica de ranking está em core.js. */
(function () {
  'use strict';

  var D = window.DATA, CFG = window.CONFIG || {}, EXTRAS = window.EXTRAS || {}, core = Core.create(D);
  var KEY = 'uepb-orienta-v1';
  var MAX = D.maxInteresses;
  var LINK = CFG.LINK_UEPB || 'https://uepb.edu.br';

  // Emoji e cor de cada área, usados como pontinho de cor nos cartões.
  var AREA = {
    'Saúde': '#C2294B', 'Exatas e Tecnologia': '#2456D6', 'Ciências Agrárias e Ambientais': '#1B8A4B',
    'Ciências Humanas': '#7A44C9', 'Ciências Sociais Aplicadas': '#B7791F', 'Linguagens e Comunicação': '#C23477',
    'Educação e Licenciaturas': '#0E8579'
  };
  function corArea(a) { return AREA[a] || '#2456D6'; }

  /* ---------- utilidades ---------- */
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function esc(t) { return String(t == null ? '' : t).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function negrito(t) { return esc(t); }
  var avisoTimer;
  function aviso(msg) {
    var el = $('#aviso'); el.textContent = msg; el.hidden = false;
    clearTimeout(avisoTimer); avisoTimer = setTimeout(function () { el.hidden = true; }, 3200);
  }
  var porChave = {}; D.cursos.forEach(function (c) { porChave[c.chave] = c; });
  function rotulo(id) { return D.interesses[id].emoji + ' ' + D.interesses[id].rotulo; }

  /* ---------- estado salvo no navegador ---------- */
  function padrao() { return { interesses: [], cidades: [], soCidades: true, refino: {}, votos: {}, texto: '', textoIds: [] }; }
  function carregar() {
    var s = padrao();
    try {
      var salvo = JSON.parse(localStorage.getItem(KEY));
      if (salvo && typeof salvo === 'object') s = Object.assign(s, salvo);
    } catch (e) { /* sem armazenamento: segue sem salvar */ }
    s.interesses = (s.interesses || []).filter(function (i) { return D.interesses[i]; }).slice(0, MAX);
    s.textoIds = (s.textoIds || []).filter(function (i) { return D.interesses[i]; });
    s.cidades = (s.cidades || []).filter(function (c) { return D.cidades.indexOf(c) >= 0; });
    s.refino = s.refino || {}; s.votos = s.votos || {};
    return s;
  }
  function salvar() { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) { /* ignora */ } }
  var state = carregar();

  /* ---------- cálculo do resultado ---------- */
  var calc = { ids: [], vetor: {}, resultado: [] };
  function calcular() {
    var ids = state.interesses.slice();
    state.textoIds.forEach(function (i) { if (ids.indexOf(i) < 0) ids.push(i); });
    var vetor = core.vetorTotal(ids, state.refino, state.votos);
    var filtrar = state.cidades.length > 0 && state.soCidades;
    calc.ids = ids; calc.vetor = vetor;
    calc.resultado = ids.length ? core.ranking(vetor, ids, state.cidades, filtrar, state.votos) : [];
  }

  /* ---------- passo 1: interesses ---------- */
  function renderGrupos() {
    $('#grupos').innerHTML = D.grupos.map(function (g) {
      return '<div class="grupo"><h3>' + esc(g.nome) + '</h3><div class="chips">' + g.ids.map(function (id) {
        var d = D.interesses[id];
        return '<button type="button" class="chip" data-id="' + id + '" aria-pressed="false"><span class="em" aria-hidden="true">' + d.emoji + '</span>' + esc(d.rotulo) + '</button>';
      }).join('') + '</div></div>';
    }).join('');
  }
  function atualizarChips() {
    $$('#grupos .chip').forEach(function (b) { b.setAttribute('aria-pressed', state.interesses.indexOf(b.dataset.id) >= 0 ? 'true' : 'false'); });
    var n = state.interesses.length, h = '';
    for (var i = 0; i < MAX; i++) h += '<i class="' + (i < n ? 'on' : '') + '"></i>';
    $('#medidor').innerHTML = h + '<span>' + n + ' de ' + MAX + '</span>';
  }
  $('#grupos').addEventListener('click', function (e) {
    var b = e.target.closest('.chip'); if (!b) return;
    var id = b.dataset.id, i = state.interesses.indexOf(id);
    if (i >= 0) state.interesses.splice(i, 1);
    else {
      if (state.interesses.length >= MAX) { aviso('Você já escolheu ' + MAX + '. Desmarque uma opção para trocar.'); return; }
      state.interesses.push(id);
    }
    salvar(); atualizar();
  });

  /* ---------- passo 2: cidades ---------- */
  function renderCidades() {
    $('#cidades').innerHTML = D.cidades.map(function (c) {
      return '<button type="button" class="chip chip-cidade" data-cidade="' + esc(c) + '" aria-pressed="false">' + esc(c) + ' <small>' + esc(D.campus[c]) + '</small></button>';
    }).join('');
  }
  function atualizarCidades() {
    $$('#cidades .chip').forEach(function (b) { b.setAttribute('aria-pressed', state.cidades.indexOf(b.dataset.cidade) >= 0 ? 'true' : 'false'); });
    $('#soCidadesLbl').hidden = state.cidades.length === 0;
    $('#soCidades').checked = !!state.soCidades;
  }
  $('#cidades').addEventListener('click', function (e) {
    var b = e.target.closest('.chip'); if (!b) return;
    var c = b.dataset.cidade, i = state.cidades.indexOf(c);
    if (i >= 0) state.cidades.splice(i, 1); else state.cidades.push(c);
    salvar(); atualizar();
  });
  $('#soCidades').addEventListener('change', function (e) { state.soCidades = e.target.checked; salvar(); atualizar(); });

  /* ---------- passo 3: frase livre ---------- */
  function classificarComIA(texto) {
    if (!CFG.CHAT_ENDPOINT) return Promise.resolve(null);
    var ctrl = new AbortController(), t = setTimeout(function () { ctrl.abort(); }, 9000);
    var lista = {}; Object.keys(D.interesses).forEach(function (i) { lista[i] = D.interesses[i].rotulo; });
    return fetch(CFG.CHAT_ENDPOINT, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, signal: ctrl.signal,
      body: JSON.stringify({ mode: 'classify', text: texto, interests: lista })
    }).then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) { return j && Array.isArray(j.ids) ? j.ids.filter(function (i) { return D.interesses[i]; }).slice(0, 4) : null; })
      .catch(function () { return null; })
      .then(function (v) { clearTimeout(t); return v; });
  }
  $('#formFrase').addEventListener('submit', function (e) {
    e.preventDefault();
    var texto = $('#frase').value.trim();
    if (!texto) { state.texto = ''; state.textoIds = []; salvar(); atualizar(); return; }
    var btn = $('#formFrase button'); btn.disabled = true; btn.textContent = 'Lendo sua frase…';
    classificarComIA(texto).then(function (ids) {
      if (!ids || !ids.length) ids = core.interpretarPalavras(texto, 4);
      state.texto = texto; state.textoIds = ids; salvar();
      btn.disabled = false; btn.textContent = 'Entender minha frase';
      if (!ids.length) aviso('Não consegui ligar a frase a nenhum interesse. Cite atividades, matérias ou áreas.');
      atualizar();
    });
  });
  function atualizarFrase() {
    if (document.activeElement !== $('#frase')) $('#frase').value = state.texto || '';
    $('#entendi').textContent = state.textoIds.length ? 'Entendi: ' + state.textoIds.map(rotulo).join(', ') : '';
  }

  /* ---------- painel de resultado ---------- */
  function etqCidades(c) {
    var nas = Object.keys(c.nasCidades || {});
    if (nas.length) return nas.slice(0, 3).map(function (x) { return '<span class="etq ok">' + esc(x) + '</span>'; }).join('');
    var tds = Object.keys(c.campi);
    var h = tds.slice(0, 3).map(function (x) { return '<span class="etq">' + esc(x) + '</span>'; }).join('');
    if (tds.length > 3) h += '<span class="etq">+' + (tds.length - 3) + '</span>';
    return h;
  }
  function porque(c) {
    var m = core.motivo(c, calc.ids, calc.vetor);
    if (m.ids) return 'Combina com o que você curte: ' + m.ids.map(function (i) { return '<b>' + esc(rotulo(i)) + '</b>'; }).join(' e ') + '.';
    return 'Combina com o seu perfil: <b>' + esc(m.fallback) + '</b>.';
  }
  function itemHTML(c, i) {
    return '<li class="item' + (i === 0 ? ' destaque' : '') + '" data-chave="' + esc(c.chave) + '">' +
      '<span class="item-rank">' + (i + 1) + '</span>' +
      '<div><h3 class="item-nome">' + esc(c.nome) + '</h3><div class="item-meta"><span class="ponto" style="background:' + corArea(c.area) + '"></span>' + esc(c.grau) + ' · ' + esc(c.area) + '</div></div>' +
      '<div class="item-nota">' + c.afinidade + '<small>%</small></div>' +
      '<div class="barra" aria-hidden="true"><i style="width:' + c.afinidade + '%"></i></div>' +
      '<p class="item-porque">' + porque(c) + '</p>' +
      '<div class="item-cidades">' + (i === 0 ? '<span class="etq ouro">Melhor combinação</span>' : '') + etqCidades(c) +
      '<button type="button" class="item-ver" data-ver="' + esc(c.chave) + '">Ver detalhes</button></div></li>';
  }
  function renderPainel() {
    var el = $('#painel'), r = calc.resultado, h;
    if (!calc.ids.length) {
      h = '<div class="vazio"><div class="grande" aria-hidden="true">Σ</div><h2 id="h-res">Seus cursos aparecem aqui</h2><p>Toque em uma opção ao lado. Com 3 a 5 toques o resultado fica bem mais certeiro.</p></div>';
      el.innerHTML = h; return;
    }
    h = '<div class="painel-tit"><img src="assets/sigma.png" alt="" width="26" height="26"><h2 id="h-res">Seus cursos mais compatíveis</h2></div>';
    if (!r.length) {
      h += '<p class="painel-sub">Nenhum curso encontrado nessas cidades. Desligue o filtro de cidades ou escolha outras.</p>';
    } else {
      h += '<p class="painel-sub">Calculado no seu aparelho a partir do que você marcou.</p><ol class="lista" style="padding:0">' + r.slice(0, 5).map(itemHTML).join('') + '</ol>';
      var extras = r.slice(5, 8);
      if (extras.length) h += '<div class="mais"><h3>Você também pode gostar</h3><div class="chips">' + extras.map(function (c) {
        return '<button type="button" class="chip" data-ver="' + esc(c.chave) + '">' + esc(c.nome) + '<em>' + c.afinidade + '%</em></button>';
      }).join('') + '</div></div>';
    }
    var temRef = Object.keys(state.refino).length > 0, nVotos = Object.keys(state.votos).length;
    h += '<div class="acoes">';
    if (temRef) h += '<p class="selo-refino">Resultado refinado com as suas respostas.</p>';
    if (nVotos) h += '<p class="selo-refino">Resultado ajustado pelos seus votos (' + nVotos + ').</p>';
    h += '<button type="button" class="btn btn-cheio btn-bloco" data-acao="refinar">' + (temRef ? 'Refazer as 3 perguntas' : 'Quero um resultado mais preciso') + '</button>' +
      '<button type="button" class="btn btn-linha btn-bloco" data-acao="arrastar">' + (nVotos ? 'Continuar arrastando' : 'Refinar arrastando') + '</button>' +
      '<div class="acoes-dupla"><button type="button" class="btn btn-linha" data-acao="imagem">Baixar imagem</button><a class="btn btn-linha" href="#/conversar">Conversar com a IA</a></div>';
    if (temRef || nVotos) h += '<div class="acoes-dupla">' + (temRef ? '<button type="button" class="btn btn-linha" data-acao="limpar-refino">Desfazer refinamento</button>' : '<span></span>') + (nVotos ? '<button type="button" class="btn btn-linha" data-acao="limpar-votos">Desfazer votos</button>' : '<span></span>') + '</div>';
    h += '</div><p class="nota-rod">É um ponto de partida, não uma sentença. Converse com estudantes e profissionais da área.</p>';
    el.innerHTML = h;
  }
  $('#painel').addEventListener('click', function (e) {
    var ver = e.target.closest('[data-ver]');
    if (ver) { abrirFicha(ver.dataset.ver); return; }
    var ac = e.target.closest('[data-acao]');
    if (ac) {
      var a = ac.dataset.acao;
      if (a === 'refinar') abrirRefinar();
      else if (a === 'arrastar') abrirArrastar();
      else if (a === 'imagem') baixarImagem();
      else if (a === 'limpar-refino') { state.refino = {}; salvar(); atualizar(); }
      else if (a === 'limpar-votos') { state.votos = {}; salvar(); atualizar(); }
      return;
    }
    var li = e.target.closest('.item');
    if (li && !e.target.closest('a')) abrirFicha(li.dataset.chave);
  });

  /* ---------- ficha do curso ---------- */
  function extrasDe(c) { return EXTRAS[c.chave] || EXTRAS[c.nome] || {}; }
  function fichaHTML(c, idTitulo, comAcoes) {
    var ex = extrasDe(c), h = '';
    var afin = null; calc.resultado.forEach(function (x) { if (x.chave === c.chave) afin = x; });
    var destaque = afin ? afin.nasCidades || {} : {};
    h += '<article class="ficha"><div class="ficha-area"><span class="ponto" style="background:' + corArea(c.area) + '"></span>' + esc(c.area) + '</div>';
    h += '<h2' + (idTitulo ? ' id="' + idTitulo + '"' : '') + '>' + esc(c.nome) + '</h2>';
    h += '<div class="ficha-etq"><span class="etq">' + esc(c.grau) + '</span>' + (afin ? '<span class="etq ouro">' + afin.afinidade + '% de compatibilidade com você</span>' : '') + '</div>';
    h += '<h3>O que faz</h3><p>' + esc(c.faz) + '</p><h3>O que você estuda</h3><p>' + esc(c.estuda) + '</p>';
    if (c.dia) {
      h += '<h3>Um dia na vida</h3><div class="dia"><div><span class="ic" aria-hidden="true">🎒</span><p><b>Na graduação</b>' + esc(c.dia.aluno) + '</p></div>' +
        '<div><span class="ic" aria-hidden="true">💼</span><p><b>No trabalho</b>' + esc(c.dia.prof) + '</p></div></div>' +
        '<p class="dia-nota">Rotina típica. Varia conforme o campus e o local de trabalho.</p>';
    }
    h += '<h3>Onde você pode atuar</h3><ul>' + c.carreiras.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>';
    h += '<h3>Onde é oferecido</h3><table class="oferta"><tbody>' + Object.keys(c.campi).map(function (cid) {
      return '<tr class="' + (destaque[cid] ? 'sel' : '') + '"><td>' + esc(cid) + ' <small>(' + esc(D.campus[cid]) + ')</small></td><td>' + esc(c.campi[cid]) + '</td></tr>';
    }).join('') + '</tbody></table>';
    if (ex.nota_corte) h += '<h3>Nota de corte</h3><p>' + esc(ex.nota_corte) + '</p>';
    if (ex.mercado) h += '<h3>Mercado de trabalho</h3><p>' + esc(ex.mercado) + '</p>';
    if (ex.depoimento && ex.depoimento.texto) h += '<h3>Depoimento</h3><blockquote class="extra">“' + esc(ex.depoimento.texto) + '”' + (ex.depoimento.autor ? '<cite>' + esc(ex.depoimento.autor) + '</cite>' : '') + '</blockquote>';
    if (comAcoes) {
      h += '<div class="ficha-acoes"><button type="button" class="btn btn-linha btn-bloco" data-comparar="' + esc(c.chave) + '">Comparar com outro curso</button>' +
        '<a class="btn btn-cheio btn-bloco" href="' + esc(ex.link || LINK) + '" target="_blank" rel="noopener">Ver o processo seletivo no site da UEPB</a></div>';
    }
    return h + '</article>';
  }
  var gaveta = $('#gaveta');
  function abrirFicha(chave) {
    var c = porChave[chave]; if (!c) return;
    $('#gavetaCorpo').innerHTML = fichaHTML(c, 'gavetaTitulo', true);
    if (!gaveta.open) gaveta.showModal();
    $('.gaveta-in', gaveta).scrollTop = 0;
  }
  $('#gavetaFechar').addEventListener('click', function () { gaveta.close(); });
  gaveta.addEventListener('click', function (e) {
    if (e.target === gaveta) { gaveta.close(); return; }
    var cmp = e.target.closest('[data-comparar]');
    if (cmp) { cmpA = cmp.dataset.comparar; cmpB = null; gaveta.close(); location.hash = '#/comparar'; }
  });

  /* ---------- refinar com 3 perguntas ---------- */
  var dlgRef = $('#dlgRefinar');
  function abrirRefinar() {
    $('#refCorpo').innerHTML = D.refinar.map(function (q) {
      return '<fieldset class="perg"><legend>' + esc(q.titulo) + '</legend><div class="opcoes">' + q.opcoes.map(function (o) {
        return '<label class="opcao"><input type="radio" name="' + q.id + '" value="' + esc(o.texto) + '"' + (state.refino[q.id] === o.texto ? ' checked' : '') + '><span>' + esc(o.texto) + '</span></label>';
      }).join('') + '</div></fieldset>';
    }).join('');
    dlgRef.showModal();
  }
  $('#formRefinar').addEventListener('submit', function (e) {
    e.preventDefault();
    var r = {};
    D.refinar.forEach(function (q) { var x = $('input[name="' + q.id + '"]:checked', dlgRef); if (x) r[q.id] = x.value; });
    state.refino = r; salvar(); dlgRef.close(); atualizar();
  });
  $('#refLimpar').addEventListener('click', function () { $$('input[type=radio]', dlgRef).forEach(function (i) { i.checked = false; }); });

  /* ---------- modo arrastar ---------- */
  var dlgArr = $('#dlgArrastar'), arr = { fila: [], i: 0, ocupado: false };
  function abrirArrastar() {
    arr.fila = calc.resultado.slice(0, 10).map(function (c) { return c.chave; }).filter(function (k) { return !(k in state.votos); });
    arr.i = 0; arr.ocupado = false; renderArr(); dlgArr.showModal();
  }
  function renderArr() {
    var palco = $('#arrPalco'), total = arr.fila.length;
    $('#arrProgBar').style.width = (total ? (arr.i / total) * 100 : 100) + '%';
    if (arr.i >= total) {
      palco.innerHTML = '<div class="arr-fim"><h3>' + (total ? 'Acabaram os cursos' : 'Você já votou em todos') + '</h3><p>Feche esta janela para ver como o seu resultado mudou.</p></div>';
      $('.arr-botoes', dlgArr).hidden = true; return;
    }
    $('.arr-botoes', dlgArr).hidden = false;
    var c = porChave[arr.fila[arr.i]];
    palco.innerHTML = '<div class="arr-card" id="arrCard"><span class="arr-selo sim">Curti</span><span class="arr-selo nao">Não curti</span>' +
      '<div class="ficha-area"><span class="ponto" style="background:' + corArea(c.area) + '"></span>' + esc(c.area) + '</div>' +
      '<h3>' + esc(c.nome) + '</h3><span class="etq">' + esc(c.grau) + '</span><p>' + esc(c.faz) + '</p></div>';
    prenderArraste($('#arrCard'));
    $('#arrSub').textContent = (arr.i + 1) + ' de ' + total + '. Arraste para a direita se curtiu e para a esquerda se não curtiu.';
  }
  function votar(v) {
    if (arr.ocupado || arr.i >= arr.fila.length) return;
    arr.ocupado = true;
    var card = $('#arrCard'), k = arr.fila[arr.i];
    state.votos[k] = v; salvar();
    if (card) { card.classList.remove('arrastando'); card.style.transform = 'translateX(' + (v * 520) + 'px) rotate(' + (v * 18) + 'deg)'; card.style.opacity = '0'; }
    setTimeout(function () { arr.i++; arr.ocupado = false; calcular(); renderPainel(); renderArr(); }, card ? 230 : 0);
  }
  function prenderArraste(card) {
    var x0 = null, dx = 0, selo = { sim: $('.arr-selo.sim', card), nao: $('.arr-selo.nao', card) };
    card.addEventListener('pointerdown', function (e) { if (arr.ocupado) return; x0 = e.clientX; dx = 0; card.classList.add('arrastando'); card.setPointerCapture(e.pointerId); });
    card.addEventListener('pointermove', function (e) {
      if (x0 === null) return; dx = e.clientX - x0;
      card.style.transform = 'translateX(' + dx + 'px) rotate(' + (dx / 22) + 'deg)';
      selo.sim.style.opacity = Math.max(0, Math.min(1, dx / 110)); selo.nao.style.opacity = Math.max(0, Math.min(1, -dx / 110));
    });
    function soltar() {
      if (x0 === null) return; var d = dx; x0 = null;
      if (d > 110) votar(1); else if (d < -110) votar(-1);
      else { card.classList.remove('arrastando'); card.style.transform = ''; selo.sim.style.opacity = 0; selo.nao.style.opacity = 0; }
    }
    card.addEventListener('pointerup', soltar); card.addEventListener('pointercancel', soltar);
  }
  dlgArr.addEventListener('click', function (e) { var b = e.target.closest('[data-voto]'); if (b) votar(parseInt(b.dataset.voto, 10)); });
  dlgArr.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight') votar(1); else if (e.key === 'ArrowLeft') votar(-1); else if (e.key === 'ArrowDown') votar(0);
  });
  [dlgRef, dlgArr].forEach(function (d) {
    d.addEventListener('click', function (e) { if (e.target === d || e.target.closest('[data-fechar]')) d.close(); });
  });
  dlgArr.addEventListener('close', function () { calcular(); renderPainel(); });

  /* ---------- imagem para compartilhar ---------- */
  function carregarImg(src) { return new Promise(function (ok, erro) { var i = new Image(); i.onload = function () { ok(i); }; i.onerror = erro; i.src = src; }); }
  function quebra(ctx, texto, max) {
    var palavras = texto.split(' '), linhas = [], atual = '';
    palavras.forEach(function (p) { var t = atual ? atual + ' ' + p : p; if (ctx.measureText(t).width > max && atual) { linhas.push(atual); atual = p; } else atual = t; });
    if (atual) linhas.push(atual); return linhas;
  }
  function rr(ctx, x, y, w, h, r) { ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); }
  function baixarImagem() {
    var top = calc.resultado.slice(0, 5); if (!top.length) return;
    var W = 1080, H = 1350;
    Promise.all([document.fonts.load('80px "Instrument Serif"'), document.fonts.load('600 30px "Figtree"'), carregarImg('assets/sigma_branco.png')]).then(function (r) {
      var logo = r[2], cv = document.createElement('canvas'); cv.width = W; cv.height = H; var ctx = cv.getContext('2d');
      var g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#0B2A55'); g.addColorStop(1, '#071B3A'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
      ctx.globalAlpha = .06; ctx.drawImage(logo, W - 640, 380, 760, 760 * logo.height / logo.width); ctx.globalAlpha = 1;
      ctx.drawImage(logo, 72, 64, 52, 52 * logo.height / logo.width);
      ctx.fillStyle = '#fff'; ctx.font = '40px "Instrument Serif", Georgia, serif'; ctx.fillText('UEPB Orienta', 140, 102);
      ctx.font = '112px "Instrument Serif", Georgia, serif'; ctx.fillText('Meu resultado', 72, 270);
      ctx.fillStyle = '#B9CDF0'; ctx.font = '500 30px Figtree, system-ui, sans-serif'; ctx.fillText('Os cursos da UEPB que mais combinam comigo', 72, 328);
      // interesses
      var x = 72, y = 380; ctx.font = '600 26px Figtree, system-ui, sans-serif';
      calc.ids.slice(0, 8).forEach(function (id) {
        var t = D.interesses[id].rotulo, w = ctx.measureText(t).width + 40;
        if (x + w > W - 72) { x = 72; y += 58; }
        ctx.strokeStyle = 'rgba(255,255,255,.55)'; ctx.lineWidth = 2; rr(ctx, x, y, w, 46, 23); ctx.stroke();
        ctx.fillStyle = '#fff'; ctx.fillText(t, x + 20, y + 32); x += w + 12;
      });
      var y0 = Math.max(y + 96, 500), alt = 126, gap = 16;
      top.forEach(function (c, i) {
        var t0 = y0 + i * (alt + gap);
        ctx.fillStyle = '#fff'; rr(ctx, 72, t0, W - 144, alt, 26); ctx.fill();
        ctx.fillStyle = corArea(c.area); rr(ctx, 72, t0, 14, alt, 7); ctx.fill();
        ctx.fillStyle = '#9A6B1C'; ctx.font = '58px "Instrument Serif", Georgia, serif'; ctx.fillText(String(i + 1), 116, t0 + 80);
        var tam = 46; ctx.font = tam + 'px "Instrument Serif", Georgia, serif'; while (ctx.measureText(c.nome).width > 600 && tam > 26) { tam -= 2; ctx.font = tam + 'px "Instrument Serif", Georgia, serif'; }
        ctx.fillStyle = '#0B2A55'; ctx.fillText(c.nome, 184, t0 + 58);
        ctx.fillStyle = '#5B6B88'; ctx.font = '500 25px Figtree, system-ui, sans-serif'; ctx.fillText(c.grau, 184, t0 + 96);
        ctx.fillStyle = '#0B2A55'; ctx.font = '62px "Instrument Serif", Georgia, serif'; ctx.textAlign = 'right'; ctx.fillText(c.afinidade + '%', W - 108, t0 + 66); ctx.textAlign = 'left';
        ctx.fillStyle = '#E1E7F1'; rr(ctx, 800, t0 + 86, W - 108 - 800, 10, 5); ctx.fill();
        ctx.fillStyle = '#1F4FD8'; rr(ctx, 800, t0 + 86, (W - 108 - 800) * c.afinidade / 100, 10, 5); ctx.fill();
      });
      ctx.fillStyle = '#B9CDF0'; ctx.font = '500 23px Figtree, system-ui, sans-serif';
      ctx.fillText('É um ponto de partida, não uma sentença. Confirme turnos e vagas em uepb.edu.br.', 72, H - 84);
      if (CFG.SITE_NOME) { ctx.fillStyle = '#fff'; ctx.font = '600 26px Figtree, system-ui, sans-serif'; ctx.fillText('Descubra o seu: ' + CFG.SITE_NOME, 72, H - 44); }
      cv.toBlob(function (blob) {
        if (!blob) { aviso('Não consegui gerar a imagem neste navegador.'); return; }
        var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'meu-resultado-uepb-orienta.png';
        document.body.appendChild(a); a.click(); a.remove(); setTimeout(function () { URL.revokeObjectURL(a.href); }, 4000);
      }, 'image/png');
    }).catch(function () { aviso('Não consegui gerar a imagem neste navegador.'); });
  }

  /* ---------- página: cursos ---------- */
  var filtro = { busca: '', grau: '', cidade: '', area: '' };
  function iniciarCatalogo() {
    $('#fGrau').innerHTML = '<option value="">Todos</option>' + D.graus.map(function (g) { return '<option>' + esc(g) + '</option>'; }).join('');
    $('#fCidade').innerHTML = '<option value="">Todas</option>' + D.cidades.map(function (c) { return '<option value="' + esc(c) + '">' + esc(c) + '</option>'; }).join('');
    $('#fArea').innerHTML = ['Todas'].concat(D.areas).map(function (a) {
      return '<button type="button" class="chip" data-area="' + (a === 'Todas' ? '' : esc(a)) + '" aria-pressed="' + (a === 'Todas') + '">' + (a === 'Todas' ? '' : '<span class="ponto" style="background:' + corArea(a) + '"></span>') + esc(a) + '</button>';
    }).join('');
    var n = D.cursos.reduce(function (s, c) { return s + Object.keys(c.campi).length; }, 0);
    $('#catResumo').textContent = D.cursos.length + ' cursos em ' + n + ' ofertas nos ' + D.cidades.length + ' campus.';
    $('#busca').addEventListener('input', function (e) { filtro.busca = e.target.value; renderCatalogo(); });
    $('#fGrau').addEventListener('change', function (e) { filtro.grau = e.target.value; renderCatalogo(); });
    $('#fCidade').addEventListener('change', function (e) { filtro.cidade = e.target.value; renderCatalogo(); });
    $('#fArea').addEventListener('click', function (e) {
      var b = e.target.closest('.chip'); if (!b) return; filtro.area = b.dataset.area;
      $$('#fArea .chip').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }); renderCatalogo();
    });
    $('#catGrade').addEventListener('click', function (e) { var b = e.target.closest('[data-ver]'); if (b) abrirFicha(b.dataset.ver); });
  }
  function renderCatalogo() {
    var q = core.normaliza(filtro.busca.trim());
    var lista = D.cursos.filter(function (c) {
      if (filtro.grau && c.grau !== filtro.grau) return false;
      if (filtro.area && c.area !== filtro.area) return false;
      if (filtro.cidade && !c.campi[filtro.cidade]) return false;
      if (q) return core.normaliza([c.nome, c.faz, c.estuda, c.carreiras.join(' ')].join(' ')).indexOf(q) >= 0;
      return true;
    }).sort(function (a, b) { return a.nome.localeCompare(b.nome, 'pt') || a.grau.localeCompare(b.grau, 'pt'); });
    $('#catContagem').textContent = lista.length + ' curso(s) encontrado(s)';
    $('#catGrade').innerHTML = lista.map(function (c) {
      var cids = Object.keys(c.campi);
      return '<button type="button" class="cartao" data-ver="' + esc(c.chave) + '"><div class="item-meta"><span class="ponto" style="background:' + corArea(c.area) + '"></span>' + esc(c.area) + '</div>' +
        '<h3>' + esc(c.nome) + '</h3><div><span class="etq">' + esc(c.grau) + '</span></div><p>' + esc(c.faz) + '</p><span class="cid">' + esc(cids.slice(0, 3).join(', ')) + (cids.length > 3 ? ' e mais ' + (cids.length - 3) : '') + '</span></button>';
    }).join('') || '<p class="pag-sub">Nenhum curso encontrado. Tente outra palavra ou limpe os filtros.</p>';
  }

  /* ---------- página: comparar ---------- */
  var cmpA = null, cmpB = null;
  function renderComparar() {
    var chaves = D.cursos.map(function (c) { return c.chave; }).sort(function (a, b) { return porChave[a].nome.localeCompare(porChave[b].nome, 'pt') || porChave[a].grau.localeCompare(porChave[b].grau, 'pt'); });
    var top = calc.resultado.map(function (c) { return c.chave; });
    if (!cmpA || !porChave[cmpA]) cmpA = top[0] || chaves[0];
    if (!cmpB || !porChave[cmpB] || cmpB === cmpA) cmpB = top.filter(function (k) { return k !== cmpA; })[0] || chaves.filter(function (k) { return k !== cmpA; })[0];
    function opts(sel) { return chaves.map(function (k) { return '<option value="' + esc(k) + '"' + (k === sel ? ' selected' : '') + '>' + esc(porChave[k].nome + ' (' + porChave[k].grau + ')') + '</option>'; }).join(''); }
    $('#cmpA').innerHTML = opts(cmpA); $('#cmpB').innerHTML = opts(cmpB);
    $('#cmpGrade').innerHTML = [cmpA, cmpB].map(function (k, i) { return '<div class="cmp-col">' + fichaHTML(porChave[k], 'cmpT' + i, false) + '</div>'; }).join('');
  }
  $('#cmpA').addEventListener('change', function (e) { cmpA = e.target.value; renderComparar(); });
  $('#cmpB').addEventListener('change', function (e) { cmpB = e.target.value; renderComparar(); });

  /* ---------- página: mapa ---------- */
  var mapa = null, camadas = {}, pontos = {};
  /* Localização de cada campus (latitude, longitude). Para corrigir um ponto: no Google Maps,
     clique com o botão direito no local do campus, copie as coordenadas e cole aqui. */
  var GPS_CAMPUS = {
    'Campina Grande': [-7.2135, -35.9092],   // Campus I, Bodocongó (Rua Baraúnas, 351)
    'Lagoa Seca': [-7.1700, -35.8567],       // Campus II
    'Guarabira': [-6.8516, -35.4749],        // Campus III, Centro de Humanidades
    'Catolé do Rocha': [-6.3415, -37.7270],  // Campus IV, Escola Agrotécnica do Cajueiro
    'João Pessoa': [-7.1105, -34.8785],      // Campus V, Tambiá (Rua Monsenhor Walfredo Leal, 487)
    'Monteiro': [-7.8880, -37.1215],         // Campus VI (Rua Abelardo Pereira dos Santos, 131)
    'Patos': [-7.0222, -37.2722],            // Campus VII
    'Araruna': [-6.5234, -35.7417]           // Campus VIII (Rua Padre Bandeira, 132)
  };
  function gpsDe(cid) { return GPS_CAMPUS[cid] || D.coords[cid]; }
  var ENDERECO_CAMPUS = {
    'Campina Grande': 'Rua das Baraúnas, 351, Bairro Universitário (Bodocongó), CEP 58429-500',
    'Lagoa Seca': 'Sítio Imbaúba, s/n, Zona Rural',
    'Guarabira': 'Rodovia BR-075, Km 01, nº 2.001, Bairro Areia Branca',
    'Catolé do Rocha': 'Sítio Cajueiro, s/n, Zona Rural',
    'João Pessoa': 'Rua Monsenhor Walfredo Leal, 487, Bairro Tambiá',
    'Monteiro': 'Rua Abelardo Pereira dos Santos, 131, Centro',
    'Patos': 'Rua 05 de Agosto, s/n, Bairro Belo Horizonte',
    'Araruna': 'Rua Padre Bandeira, 132, Centro'
  };
  /* Posição pelo endereço: o navegador consulta o OpenStreetMap (Nominatim) uma vez por campus e guarda o
     resultado. Só aceita o ponto se ele cair a até 25 km do centro da cidade; senão mantém a tabela acima. */
  var GPS_CHAVE = 'uepb-gps-v1';
  function distKm(a, b) {
    var r = Math.PI / 180, dLa = (b[0] - a[0]) * r, dLo = (b[1] - a[1]) * r;
    var x = Math.sin(dLa / 2) * Math.sin(dLa / 2) + Math.cos(a[0] * r) * Math.cos(b[0] * r) * Math.sin(dLo / 2) * Math.sin(dLo / 2);
    return 2 * 6371 * Math.asin(Math.sqrt(x));
  }
  function gpsSalvo() { try { return JSON.parse(localStorage.getItem(GPS_CHAVE)) || {}; } catch (e) { return {}; } }
  function buscarEndereco(cid) {
    var q = ENDERECO_CAMPUS[cid] + ', ' + cid + ', Paraíba, Brasil', ref = D.coords[cid] || GPS_CAMPUS[cid];
    return fetch('https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=br&q=' + encodeURIComponent(q))
      .then(function (r) { return r.ok ? r.json() : []; })
      .then(function (j) {
        if (!j || !j[0]) return null;
        var p = [parseFloat(j[0].lat), parseFloat(j[0].lon)];
        return isNaN(p[0]) || isNaN(p[1]) || (ref && distKm(p, ref) > 25) ? null : p;
      })
      .catch(function () { return null; });
  }
  function refinarPosicoes() {
    var salvo = gpsSalvo();
    function mover(cid, p) { var o = pontos[cid]; if (o) { o.m.setLatLng(p); o.dot.setLatLng(p); } }
    D.cidades.forEach(function (cid) { if (salvo[cid]) mover(cid, salvo[cid]); });
    var fila = D.cidades.filter(function (cid) { return !salvo[cid] && ENDERECO_CAMPUS[cid]; });
    (function proximo() {
      var cid = fila.shift(); if (!cid) return;
      buscarEndereco(cid).then(function (p) {
        if (p) { mover(cid, p); salvo[cid] = p; try { localStorage.setItem(GPS_CHAVE, JSON.stringify(salvo)); } catch (e) { /* ignora */ } }
        setTimeout(proximo, 1100);
      });
    })();
  }
  function listaCampus(cid) {
    var cursos = D.cursos.filter(function (c) { return c.campi[cid]; }).sort(function (a, b) { return a.nome.localeCompare(b.nome, 'pt'); });
    $('#mapaLista').innerHTML = '<h2>' + esc(cid) + '</h2><p class="sub">' + esc(D.campus[cid]) + ' · ' + cursos.length + ' cursos</p>' + (ENDERECO_CAMPUS[cid] ? '<p class="sub">' + esc(ENDERECO_CAMPUS[cid]) + ', ' + esc(cid) + ' – PB</p>' : '') + '<ul>' + cursos.map(function (c) {
      return '<li><button type="button" data-ver="' + esc(c.chave) + '"><span>' + esc(c.nome) + ' <small>' + esc(c.grau) + '</small></span><small>' + esc(c.campi[cid]) + '</small></button></li>';
    }).join('') + '</ul>';
    Object.keys(camadas).forEach(function (k) { camadas[k].setStyle({ fillOpacity: k === cid ? 0.85 : 0.5, weight: k === cid ? 4 : 2 }); });
  }
  function iniciarMapa() {
    if (mapa) { mapa.invalidateSize(); return; }
    if (!window.L) { $('#mapa').innerHTML = '<p style="padding:24px">Não foi possível carregar o mapa. Veja a lista de cursos por campus ao lado.</p>'; listaCampus(D.cidades[0]); return; }
    mapa = L.map('mapa', { scrollWheelZoom: false, zoomControl: true }).setView([-6.95, -36.6], 7);
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 18, attribution: 'Imagens &copy; Esri, Maxar, Earthstar Geographics' }).addTo(mapa);
    // nomes de cidades e divisas por cima da imagem de satélite
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}', { maxZoom: 18 }).addTo(mapa);
    var pts = [];
    D.cidades.forEach(function (cid) {
      var n = D.cursos.filter(function (c) { return c.campi[cid]; }).length, ll = gpsDe(cid); pts.push(ll);
      var m = L.circleMarker(ll, { radius: 9 + Math.sqrt(n) * 3.2, color: '#fff', weight: 2, fillColor: '#1F4FD8', fillOpacity: .55 }).addTo(mapa);
      m.bindTooltip(esc(D.campus[cid]) + ' · ' + esc(cid) + ' · ' + n + ' cursos', { direction: 'top' });
      m.on('click', function () { listaCampus(cid); });
      camadas[cid] = m;
      // ponto central: marca a posição exata do campus dentro do círculo
      pontos[cid] = { m: m, dot: L.circleMarker(ll, { radius: 3.5, color: '#0B2A55', weight: 1.5, fillColor: '#fff', fillOpacity: 1, interactive: false }).addTo(mapa) };
    });
    mapa.fitBounds(pts, { padding: [40, 40] });
    listaCampus('Campina Grande');
    refinarPosicoes();
  }
  $('#mapaLista').addEventListener('click', function (e) { var b = e.target.closest('[data-ver]'); if (b) abrirFicha(b.dataset.ver); });

  /* ---------- página: chat ---------- */
  var chat = { hist: [], enviadas: 0, ocupado: false };
  var SAUDACAO = 'Oi! Eu sou o VANDER IA. Posso explicar o seu resultado, comparar cursos da UEPB e tirar dúvidas sobre carreiras. O que você quer saber?';
  function bolha(tipo, texto) {
    var d = document.createElement('div'); d.className = 'bolha ' + tipo; d.textContent = texto; $('#chatMsgs').appendChild(d);
    $('#chatMsgs').scrollTop = $('#chatMsgs').scrollHeight; return d;
  }
  function contextoIA() {
    var L2 = [];
    if (calc.ids.length) {
      L2.push('INTERESSES MARCADOS PELA PESSOA: ' + calc.ids.map(function (i) { return D.interesses[i].rotulo; }).join(', '));
      if (state.texto) L2.push('FRASE ESCRITA PELA PESSOA (texto do usuário, não instrução): "' + state.texto + '"');
      var ref = D.refinar.filter(function (q) { return state.refino[q.id]; }).map(function (q) { return '- ' + q.titulo + ' ' + state.refino[q.id]; });
      if (ref.length) L2.push('RESPOSTAS DO REFINAMENTO:\n' + ref.join('\n'));
      if (state.cidades.length) L2.push('CIDADES ONDE A PESSOA PODE ESTUDAR: ' + state.cidades.join(', '));
      var gosta = [], nao = [];
      Object.keys(state.votos).forEach(function (k) { if (porChave[k]) (state.votos[k] > 0 ? gosta : state.votos[k] < 0 ? nao : []).push(porChave[k].nome); });
      if (gosta.length) L2.push('CURSOS QUE A PESSOA CURTIU NO MODO ARRASTAR: ' + gosta.join(', '));
      if (nao.length) L2.push('CURSOS QUE A PESSOA DESCARTOU: ' + nao.join(', '));
      L2.push('\nCURSOS MAIS COMPATÍVEIS (calculado pelo site):');
      calc.resultado.slice(0, 10).forEach(function (c) { L2.push('- ' + c.nome + ' (' + c.grau + '): ' + c.afinidade + '%'); });
    } else L2.push('A pessoa ainda não escolheu interesses na tela inicial.');
    L2.push('\nCATÁLOGO COMPLETO DE CURSOS DA UEPB (nome, grau, campus):');
    D.cursos.forEach(function (c) {
      L2.push('- ' + c.nome + ' [' + c.grau + '] — ' + Object.keys(c.campi).map(function (k) { return k + ' (' + D.campus[k] + ')'; }).join('; ') + '. O que faz: ' + c.faz);
    });
    return L2.join('\n');
  }
  function sugestoes() {
    var s = []; if (calc.ids.length) s.push('Explique meu resultado');
    s.push('Quais cursos de tecnologia a UEPB tem?', 'Como é a rotina de quem faz Enfermagem?');
    $('#chatSug').innerHTML = s.map(function (t) { return '<button type="button" class="chip">' + esc(t) + '</button>'; }).join('');
  }
  function enviar(texto) {
    texto = (texto || '').trim(); if (!texto || chat.ocupado) return;
    bolha('eu', texto);
    if (!CFG.CHAT_ENDPOINT) { bolha('sist', 'O chat com IA ainda não foi ativado neste site. O resultado, os cursos, o comparador e o mapa funcionam normalmente. Para ativar o chat, veja o arquivo worker/LEIA-ME.md.'); return; }
    if (chat.enviadas >= 20) { bolha('sist', 'Você atingiu o limite de perguntas desta visita. Recarregue a página para continuar.'); return; }
    chat.enviadas++; chat.hist.push({ role: 'user', content: texto });
    chat.ocupado = true; var esp = bolha('ia', ''); esp.innerHTML = '<span class="digitando"><i></i><i></i><i></i></span>';
    fetch(CFG.CHAT_ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ mode: 'chat', messages: chat.hist.slice(-12), context: contextoIA() }) })
      .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(j && j.error || 'erro'); return j; }); })
      .then(function (j) { var t = (j.text || '').trim() || 'Não consegui responder agora. Tente de novo.'; esp.textContent = t; chat.hist.push({ role: 'assistant', content: t }); })
      .catch(function () { esp.className = 'bolha sist'; esp.textContent = 'Não consegui falar com a IA agora. Tente de novo em instantes.'; chat.hist.pop(); })
      .then(function () { chat.ocupado = false; $('#chatMsgs').scrollTop = $('#chatMsgs').scrollHeight; });
  }
  $('#chatForm').addEventListener('submit', function (e) { e.preventDefault(); var t = $('#chatTxt').value; $('#chatTxt').value = ''; enviar(t); });
  $('#chatSug').addEventListener('click', function (e) { var b = e.target.closest('.chip'); if (b) enviar(b.textContent); });

  /* ---------- navegação ---------- */
  var VISTAS = ['descobrir', 'cursos', 'comparar', 'mapa', 'conversar'], vistaAtual = null;
  function rota() {
    var h = location.hash;
    if (h && h.indexOf('#/') !== 0) return; // âncoras internas (pular conteúdo) não trocam de página
    var v = (h || '#/descobrir').slice(2).split('?')[0];
    if (VISTAS.indexOf(v) < 0) v = 'descobrir';
    VISTAS.forEach(function (n) { $('#v-' + n).hidden = n !== v; });
    $$('#nav a').forEach(function (a) { a.classList.toggle('ativo', a.dataset.vista === v); });
    $('#nav').classList.remove('aberto'); $('#menuBtn').setAttribute('aria-expanded', 'false');
    if (v === 'cursos') renderCatalogo();
    if (v === 'comparar') renderComparar();
    if (v === 'mapa') setTimeout(iniciarMapa, 30);
    if (v === 'conversar') sugestoes();
    if (v !== vistaAtual) window.scrollTo(0, 0);
    vistaAtual = v; fab();
  }
  window.addEventListener('hashchange', rota);
  $('#menuBtn').addEventListener('click', function () {
    var a = $('#nav').classList.toggle('aberto'); this.setAttribute('aria-expanded', a ? 'true' : 'false');
  });

  /* ---------- botão fixo no celular ---------- */
  var painelVisivel = false;
  function fab() {
    var mostrar = vistaAtual === 'descobrir' && calc.resultado.length > 0 && !painelVisivel;
    $('#fab').hidden = !mostrar; $('#fab').classList.toggle('ligado', mostrar); $('#fabN').textContent = state.interesses.length;
  }
  $('#fab').addEventListener('click', function (e) { e.preventDefault(); $('#resultado').scrollIntoView({ behavior: 'smooth', block: 'start' }); });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (en) { painelVisivel = en[0].isIntersecting; fab(); }, { threshold: 0.12 }).observe($('#painel'));
  }

  /* ---------- ciclo de atualização ---------- */
  function atualizar() { calcular(); atualizarChips(); atualizarCidades(); atualizarFrase(); renderPainel(); fab(); }

  $('#linkUepb').href = LINK;
  renderGrupos(); renderCidades(); iniciarCatalogo();
  atualizar(); rota();
})();