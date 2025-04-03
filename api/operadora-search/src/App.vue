<template>
  <div class="container">
    <h1>Busca de Operadoras de Saúde</h1>
    <div class="search-container">
      <div class="search-box">
        <input 
          type="text" 
          v-model="termo" 
          placeholder="Digite o nome da operadora (mínimo 3 caracteres)"
          :disabled="carregando"
          @keyup.enter="buscarOperadoras"
        />
        <button 
          @click="buscarOperadoras"
          :disabled="termo.length < 3 || carregando"
        >
          <span v-if="!carregando">🔍 Buscar</span>
          <span v-else>⌛ Buscando...</span>
        </button>
      </div>
      <div v-if="carregando" class="loading-indicator">
        <div class="spinner"></div>
        <span>Carregando resultados...</span>
      </div>
    </div>

    <div v-if="erro" class="error-message">
      <span class="error-icon">⚠️</span>
      <span>{{ erro }}</span>
    </div>

    <div v-if="operadoras.length" class="results-container">
      <div class="results-header">
        <h2>Resultados encontrados: {{ operadoras.length }}</h2>
        <div class="search-info">
          Busca por: "<strong>{{ termo }}</strong>"
        </div>
      </div>
      
      <div class="operadoras-grid">
        <div 
          v-for="(operadora, index) in operadoras" 
          :key="operadora.Registro_ANS || index" 
          class="operadora-card"
        >
          <div class="card-header">
            <h3>{{ operadora.Razao_Social || 'Nome não disponível' }}</h3>
            <span class="registro-ans" v-if="operadora.Registro_ANS">
              Registro ANS: {{ operadora.Registro_ANS }}
            </span>
          </div>
          
          <div class="card-body">
            <div class="info-row" v-if="operadora.Modalidade">
              <span class="info-label">Modalidade:</span>
              <span class="info-value">{{ operadora.Modalidade }}</span>
            </div>
            
            <div class="info-row" v-if="operadora.CNPJ">
              <span class="info-label">CNPJ:</span>
              <span class="info-value">{{ operadora.CNPJ }}</span>
            </div>
            
            <div class="info-row" v-if="operadora.Logradouro || operadora.Numero || operadora.Bairro">
              <span class="info-label">Endereço:</span>
              <span class="info-value">
                {{ operadora.Logradouro || '' }} 
                {{ operadora.Numero ? ', ' + operadora.Numero : '' }} 
                {{ operadora.Bairro ? ' - ' + operadora.Bairro : '' }}
              </span>
            </div>
            
            <div class="info-row" v-if="operadora.Cidade || operadora.UF">
              <span class="info-label">Cidade/UF:</span>
              <span class="info-value">
                {{ operadora.Cidade || '' }} 
                {{ operadora.UF ? ' - ' + operadora.UF : '' }}
              </span>
            </div>
            
            <div class="info-row" v-if="operadora.Telefone">
              <span class="info-label">Telefone:</span>
              <span class="info-value">
                {{ operadora.DDD ? '(' + operadora.DDD + ') ' : '' }}
                {{ operadora.Telefone }}
              </span>
            </div>
            
            <div class="info-row" v-if="operadora.Endereco_eletronico">
              <span class="info-label">Email:</span>
              <span class="info-value">{{ operadora.Endereco_eletronico }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else-if="termo.length >= 3 && !carregando" class="no-results">
      <div class="no-results-content">
        <span class="no-results-icon">😕</span>
        <h3>Nenhum resultado encontrado</h3>
        <p>Não encontramos operadoras com o termo "<strong>{{ termo }}</strong>"</p>
        <button @click="termo = ''; operadoras = []" class="try-again">
          Tentar nova busca
        </button>
      </div>
    </div>
    
    <div v-else-if="termo.length > 0 && termo.length < 3" class="search-hint">
      Digite pelo menos 3 caracteres para realizar a busca
    </div>
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
        return;
      }

      this.carregando = true;
      this.erro = null;
      this.operadoras = [];

      try {
        const response = await axios.get(`http://127.0.0.1:5000/buscar?termo=${encodeURIComponent(this.termo)}`);
        console.log("Dados recebidos:", response.data);
        
        // Filtra resultados que têm pelo menos um campo preenchido
        this.operadoras = response.data.filter(item => 
          Object.values(item).some(val => val !== null && val !== '')
        );
        
        if (this.operadoras.length === 0 && response.data.length > 0) {
          this.erro = "Encontramos registros, mas todos estão incompletos.";
        }
      } catch (error) {
        console.error("Erro ao buscar operadoras:", error);
        this.erro = error.response?.data?.erro || 
                   error.response?.data?.message || 
                   "Erro ao conectar com o servidor. Verifique sua conexão.";
      } finally {
        this.carregando = false;
      }
    }
  }
};
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

h1 {
  color: #2c3e50;
  text-align: center;
  margin-bottom: 2rem;
}

.search-container {
  margin-bottom: 2rem;
}

.search-box {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

input {
  flex: 1;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  border: 2px solid #ddd;
  border-radius: 8px;
  transition: border-color 0.3s;
}

input:focus {
  outline: none;
  border-color: #3498db;
}

input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

button {
  padding: 0.75rem 1.5rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover:not(:disabled) {
  background-color: #2980b9;
}

button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #7f8c8d;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: #3498db;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.error-icon {
  font-size: 1.2rem;
}

.results-container {
  margin-top: 2rem;
}

.results-header {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.search-info {
  color: #7f8c8d;
  font-style: italic;
}

.operadoras-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.operadora-card {
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s;
}

.operadora-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 1.25rem;
  background-color: #3498db;
  color: white;
}

.card-header h3 {
  margin: 0;
  font-size: 1.25rem;
}

.registro-ans {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.85rem;
  opacity: 0.9;
}

.card-body {
  padding: 1.25rem;
}

.info-row {
  display: flex;
  margin-bottom: 0.75rem;
  line-height: 1.5;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  font-weight: bold;
  min-width: 100px;
  color: #2c3e50;
}

.info-value {
  flex: 1;
  color: #34495e;
}

.no-results {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  text-align: center;
}

.no-results-content {
  max-width: 400px;
}

.no-results-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 1rem;
}

.no-results h3 {
  color: #7f8c8d;
  margin-bottom: 0.5rem;
}

.try-again {
  margin-top: 1rem;
  background-color: #95a5a6;
}

.try-again:hover {
  background-color: #7f8c8d;
}

.search-hint {
  text-align: center;
  color: #7f8c8d;
  font-style: italic;
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .container {
    padding: 1rem;
  }
  
  .search-box {
    flex-direction: column;
  }
  
  .operadoras-grid {
    grid-template-columns: 1fr;
  }
  
  .info-row {
    flex-direction: column;
  }
  
  .info-label {
    margin-bottom: 0.25rem;
  }
}
</style>