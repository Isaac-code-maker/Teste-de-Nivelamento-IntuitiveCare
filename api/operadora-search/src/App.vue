<template>
  <div class="container">
    <h1>Busca de Operadoras</h1>
    <div class="search-container">
      <input 
        type="text" 
        v-model="termo" 
         
        placeholder="Digite o nome da operadora"
        :disabled="carregando"
      />
      <div v-if="carregando" class="loading">Carregando...</div>
      <button v-on:click="buscarOperadoras">Buscar</button>  
    </div>

    <div v-if="erro" class="erro">
      {{ erro }}
    </div>

    <div v-if="operadoras.length" class="resultados">
      <div v-for="(operadora, index) in operadoras" :key="operadora.Registro_ANS || index" class="operadora-card">
        <h3>{{ operadora.Razao_Social }}</h3>
        <p>Modalidade: {{ operadora.Modalidade }}</p>
        <p>CNPJ: {{ operadora.CNPJ }}</p>
        <p>Endereço: {{ operadora.Logradouro }}, {{ operadora.Numero }} - {{ operadora.Bairro }}</p>
        <p>{{ operadora.Cidade }} - {{ operadora.UF }}</p>
        <p v-if="operadora.Telefone">Telefone: ({{ operadora.DDD }}) {{ operadora.Telefone }}</p>
        <p v-if="operadora.Endereco_eletronico">Email: {{ operadora.Endereco_eletronico }}</p>
      </div>
    </div>
    <p v-else-if="termo.length >= 3 && !carregando">Nenhum resultado encontrado.</p>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      termo: "",
      operadoras: [],
      carregando: false,
      erro: null
    };
  },
  methods: {
    async buscarOperadoras() {
      if (this.termo.length < 3) {
        this.operadoras = [];
        this.erro = null;
        return;
      }

      this.carregando = true;
      this.erro = null;

      try {
        const response = await axios.get(`http://127.0.0.1:5000/buscar?termo=${this.termo}`);
        console.log(response.data)
        this.operadoras = response.data;
      } catch (error) {
        console.error("Erro ao buscar operadoras:", error);
        this.erro = "Erro ao buscar operadoras. Verifique se o servidor está rodando.";
        this.operadoras = [];
      } finally {
        this.carregando = false;
      }
    }
  }
};
</script>

<style>
.container {
  max-width: 800px;
  margin: auto;
  padding: 20px;
}

.search-container {
  position: relative;
  margin-bottom: 20px;
}

input {
  width: 100%;
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.loading {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
}

.erro {
  background-color: #ffebee;
  color: #c62828;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.resultados {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.operadora-card {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.operadora-card h3 {
  margin-top: 0;
  color: #333;
}

.operadora-card p {
  margin: 5px 0;
  color: #666;
  font-size: 14px;
}
</style>
