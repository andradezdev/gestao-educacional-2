# Guia de Instalação e Implantação — ERPZ Educacional

Este documento detalha os requisitos de sistema, dependências e procedimentos passo a passo para instalação e configuração do aplicativo no ambiente Frappe Bench.

---

## 🚀 Requisitos de Ambiente

* **Frappe Framework:** v16.0 ou superior
* **ERPNext:** v16.0 ou superior
* **Python:** 3.10 ou superior (compatível com Python 3.14)
* **Node.js:** v18+, v20+ ou v24+ com Yarn
* **MariaDB:** 10.6 ou superior

---

## 📦 Dependências

O ERPZ Educacional utiliza o aplicativo complementar **`ifitwala_drive`** para armazenamento governado, controle seguro de laudos médicos, anexos de candidatos e mídias de portfólio protegidas.

---

## ⚙️ Procedimento de Instalação no Bench

### 1. Acessar o diretório do bench
```bash
cd ~/frappe-bench
```

### 2. Baixar o aplicativo de arquivos protegidos (`ifitwala_drive`)
```bash
bench get-app https://github.com/fderyckel/ifitwala_drive.git
```

### 3. Baixar o aplicativo ERPZ Educacional
```bash
bench get-app https://github.com/andradezdev/gestao-educacional-2.git
```

### 4. Instalar as dependências no ambiente virtual Python
```bash
bench pip install -e apps/ifitwala_drive
bench pip install -e apps/gestao-educacional-2
```

### 5. Instalar os aplicativos no site
```bash
bench --site [nome-do-site] install-app ifitwala_drive
bench --site [nome-do-site] install-app ifitwala_ed
```

### 6. Executar as migrações de metadados
```bash
bench --site [nome-do-site] migrate
```

### 7. Compilar os assets de interface (Vite SPA e Desk)
```bash
bench build --app ifitwala_ed
```

### 8. Limpar caches do sistema
```bash
bench --site [nome-do-site] clear-cache
```

---

## 🔧 Configurações Pós-Instalação

1. **Acesso pelo Desk**: O sistema cria automaticamente o ícone **ERPZ Educacional** na grade da Área de Trabalho (`/desk`), concedendo acesso centralizado a todos os módulos escolares (Acadêmico, Admissões, Secretaria, Currículo, Saúde Escolar, Extracurricular e Administração).
2. **Estrutura Inicial**: Ao iniciar o uso, cadastre a `Organização Mantenedora` e a `Escola/Campus` vinculada para habilitar o calendário letivo, turmas e matrículas.
