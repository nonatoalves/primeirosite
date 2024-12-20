const form = document.getElementById('salario-form');
const resultadoDiv = document.getElementById('resultado');

form.addEventListener('submit', (e) => {
    e.preventDefault();

    const salarioBase = parseFloat(document.getElementById('salario-base').value);
    const auxilioAlimentacao = parseFloat(document.getElementById('auxilio-alimentacao').value);
    const auxilioTransporte = parseFloat(document.getElementById('auxilio-transporte').value);
    const auxilioSaude = parseFloat(document.getElementById('auxilio-saude').value);
    const descontoIR = parseFloat(document.getElementById('desconto-ir').value);
    const descontoPrevidencia = parseFloat(document.getElementById('desconto-previdencia').value);

    const totalAuxilios = auxilioAlimentacao + auxilioTransporte + auxilioSaude;
    const salarioBruto = salarioBase + totalAuxilios;
    const descontoIRValor = salarioBruto * (descontoIR / 100);
    const descontoPrevidenciaValor = salarioBruto * (descontoPrevidencia / 100);
    const salarioLiquido = salarioBruto - descontoIRValor - descontoPrevidenciaValor;

    resultadoDiv.innerHTML = `
        Salário Base: R$ ${salarioBase.toFixed(2)}<br>
        Auxílios: R$ ${totalAuxilios.toFixed(2)}<br>
        Salário Bruto: R$ ${salarioBruto.toFixed(2)}<br>
        Desconto IR: R$ ${descontoIRValor.toFixed(2)} (${descontoIR}%)<br>
        Desconto Previdência: R$ ${descontoPrevidenciaValor.toFixed(2)} (${descontoPrevidencia}%)<br>
        Salário Líquido: R$ ${salarioLiquido.toFixed(2)}
    `;
});