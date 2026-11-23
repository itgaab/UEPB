/* Núcleo do orientador: ranking de cursos, motivo e leitura de frase livre.
   É a mesma lógica do app em Python (orientador.py), sem dependências. */
(function (root) {
  function create(DATA) {
    var DIMS = DATA.dims;

    // Arredondamento igual ao do Python (metade vai para o par mais próximo).
    function pyRound(x) {
      var f = Math.floor(x), d = x - f;
      if (d < 0.5) return f;
      if (d > 0.5) return f + 1;
      return f % 2 === 0 ? f : f + 1;
    }

    function cosseno(a, b) {
      var num = 0, na = 0, nb = 0;
      for (var i = 0; i < a.length; i++) { num += a[i] * b[i]; na += a[i] * a[i]; nb += b[i] * b[i]; }
      var den = Math.sqrt(na) * Math.sqrt(nb);
      return den ? num / den : 0;
    }

    function vetorTotal(ids, refino, votos) {
      var v = {};
      DIMS.forEach(function (d) { v[d] = 0; });
      (ids || []).forEach(function (id) {
        var iv = DATA.interesses[id].vetor;
        Object.keys(iv).forEach(function (d) { v[d] += iv[d]; });
      });
      DATA.refinar.forEach(function (q) {
        var r = refino && refino[q.id];
        if (r == null) return;
        var op = q.opcoes.find(function (o) { return o.texto === r; });
        if (op) Object.keys(op.vetor).forEach(function (d) { v[d] += op.vetor[d]; });
      });
      // Modo arrastar: curtir puxa o perfil para o curso; não curtir afasta um pouco.
      DATA.cursos.forEach(function (c) {
        var voto = votos && votos[c.chave];
        if (voto) {
          var peso = voto > 0 ? 0.6 : -0.25;
          DIMS.forEach(function (d, i) { v[d] += peso * c.perfil[i]; });
        }
      });
      DIMS.forEach(function (d) { v[d] = Math.max(0, v[d]); });
      return v;
    }

    function ehAfim(curso, id) { return DATA.interesses[id].afins.indexOf(curso.nome) >= 0; }

    function ranking(vetor, ids, cidades, soCidades, votos) {
      var u = DIMS.map(function (d) { return vetor[d]; });
      var out = [];
      DATA.cursos.forEach(function (c) {
        var nas = {};
        if (cidades && cidades.length) {
          Object.keys(c.campi).forEach(function (k) { if (cidades.indexOf(k) >= 0) nas[k] = c.campi[k]; });
        }
        var temNas = Object.keys(nas).length > 0;
        if (cidades && cidades.length && soCidades && !temNas) return;
        var voto = (votos && votos[c.chave]) || 0;
        if (voto < 0) return; // descartado no modo arrastar
        var sim = cosseno(u, c.perfil);
        var pct = 100 * sim * sim;
        var afins = 0;
        (ids || []).forEach(function (id) { if (ehAfim(c, id)) afins++; });
        pct += Math.min(DATA.bonusAfimMax, DATA.bonusAfim * afins);
        if (temNas) pct += 2;
        if (voto > 0) pct += 4;
        pct = Math.min(99, pct * 0.9);
        var item = Object.assign({}, c, { afinidade: pyRound(pct), nasCidades: nas });
        out.push(item);
      });
      out.sort(function (a, b) { return b.afinidade - a.afinidade; });
      return out;
    }

    // Devolve {ids:[até 2 interesses], fallback:"nome da dimensão"} para montar a frase "por que combina".
    function motivo(curso, ids, vetor) {
      var pont = (ids || []).map(function (id) {
        var iv = DATA.interesses[id].vetor, total = 0, s = 0;
        Object.keys(iv).forEach(function (d) { total += iv[d]; s += iv[d] * curso.perfil[DIMS.indexOf(d)]; });
        s = s / total;
        if (ehAfim(curso, id)) s += 5;
        return { s: s, id: id };
      });
      pont.sort(function (a, b) { return b.s - a.s; });
      var bons = pont.filter(function (p) { return p.s >= 2.5; }).slice(0, 2).map(function (p) { return p.id; });
      if (bons.length) return { ids: bons };
      var melhor = DIMS.slice().sort(function (a, b) {
        return vetor[b] * curso.perfil[DIMS.indexOf(b)] - vetor[a] * curso.perfil[DIMS.indexOf(a)];
      })[0];
      return { fallback: DATA.dimNomes[melhor] };
    }

    function normaliza(t) {
      return String(t).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/\s+/g, ' ');
    }

    // Plano B sem IA: encontra interesses pelas palavras da frase.
    function interpretarPalavras(texto, limite) {
      var t = ' ' + normaliza(texto) + ' ';
      var achados = [];
      Object.keys(DATA.interesses).forEach(function (id) {
        var n = 0;
        DATA.interesses[id].palavras.forEach(function (p) { if (t.indexOf(p) >= 0) n++; });
        if (n) achados.push({ n: n, id: id });
      });
      achados.sort(function (a, b) { return b.n - a.n; });
      return achados.slice(0, limite || 4).map(function (a) { return a.id; });
    }

    return { vetorTotal: vetorTotal, ranking: ranking, motivo: motivo, interpretarPalavras: interpretarPalavras, normaliza: normaliza };
  }

  if (typeof module !== 'undefined' && module.exports) module.exports = { create: create };
  else root.Core = { create: create };
})(typeof window !== 'undefined' ? window : globalThis);
