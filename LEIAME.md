# Guia de Instalação e Implantação — ERPZ Educacional

Este documento detalha os requisitos de sistema, dependências e procedimentos passo a passo para instalação e configuração do aplicativo no ambiente Frappe Bench.

---

## 🚀 Requisitos de Ambiente

* **Frappe Framework:** v16.0 ou superior
* **ERPNext:** v16.0 ou superior
* **Python:** 3.10 ou superior (totalmente compatível com Python 3.14)
* **Node.js:** v18+, v20+ ou v24+ com Yarn
* **MariaDB:** 10.6 ou superior

---

## 📦 Arquitetura Monolítica Integrada (Sem Dependências Externas)

O módulo de governança e custódia segura de arquivos (**Ifitwala Drive**) encontra-se **totalmente integrado e embutido** dentro deste próprio repositório.

Não é necessário baixar, clonar ou instalar nenhum aplicativo secundário. Uma única instalação provê todo o ecossistema educacional e de armazenamento seguro.

---

## ⚙️ Procedimento de Instalação em 1 Passo no Bench

### 1. Acessar o diretório do bench
```bash
cd ~/frappe-bench
```

### 2. Baixar o aplicativo ERPZ Educacional
```bash
bench get-app https://github.com/andradezdev/gestao-educacional-2.git
```

### 3. Instalar o aplicativo no site desejado
```bash
bench --site [nome-do-site] install-app ifitwala_ed
```

### 4. Executar as migrações de metadados
```bash
bench --site [nome-do-site] migrate
```

### 5. Compilar os assets de interface (Vite SPA e Desk)
```bash
bench build --app ifitwala_ed
```

### 6. Limpar os caches do sistema
```bash
bench --site [nome-do-site] clear-cache
```

---

## 🔧 Configurações Pós-Instalação

1. **Acesso Centralizado pelo Desk**: O sistema disponibiliza automaticamente o ícone **ERPZ Educacional** na grade principal da Área de Trabalho (`/desk`), dando acesso unificado a todos os módulos escolares (Acadêmico, Admissões, Secretaria, Currículo, Saúde Escolar, Extracurricular e Administração).
2. **Estrutura Organizacional**: Ao iniciar o uso da instituição, cadastre a `Organização Mantenedora` e a `Escola/Campus` vinculada para habilitar o calendário letivo, turmas e matrículas.
