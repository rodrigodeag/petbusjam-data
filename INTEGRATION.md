# Documentação de Integração - PetBusJam (Godot 4 & Pipeline de Dados) 🚌🐾

Esta documentação detalha a arquitetura e o fluxo de dados entre o repositório gerador **`petbusjam-data`** e o projeto do jogo **PetBusJam** (desenvolvido em Godot 4).

---

## 1. Visão Geral da Arquitetura

O projeto adota o padrão **Headless Content Delivery via CDN Estática (GitHub Raw)**:
- **Repositório de Dados (`petbusjam-data`)**: Mantém o script gerador procedural (`generator.py`) e o banco de dados oficial de fases (`levels.json`).
- **Repositório do Jogo (Godot 4)**: Consome o arquivo `levels.json` remotamente em tempo de execução via requisições HTTP, permitindo atualizar fases, balanceamentos e adicionar novos níveis sem precisar lançar uma nova build na Google Play.

---

## 2. Pipeline de Geração e Publicação de Fases

Sempre que precisar criar novos lotes de fases para o jogo:

1. **Abra o terminal** na pasta do repositório `petbusjam-data`.
2. **Execute o gerador Python** especificando a quantidade desejada (ex: `150` fases):
   ```bash
   python generator.py 150
   ```
   *(O script gera automaticamente fases balanceadas por dificuldade, com suporte a ônibus trancados e passageiros mistério, validando a integridade estrutural de cada nível).*
3. **Publique as alterações no GitHub**:
   ```bash
   git add levels.json
   git commit -m "feat: update levels.json with new generated stages"
   git push origin main
   ```

---

## 3. Integração Cliente (Godot 4)

Para consumir as fases dinamicamente no Godot 4 com resiliência a quedas de conexão (suporte offline), utilize o seguinte script Singleton/AutoLoad (ex: `LevelManager.gd`):

```gdscript
extends Node

const LEVELS_URL = "https://raw.githubusercontent.com/rodrigodeag/petbusjam-data/main/levels.json"
const LOCAL_CACHE_PATH = "user://cached_levels.json"

var level_data: Dictionary = {}
signal levels_loaded(data: Dictionary)

func _ready() -> void:
	# 1. Carrega o cache local para garantir funcionamento offline imediato
	load_local_cache()
	
	# 2. Busca a versão mais atualizada na nuvem em background
	fetch_remote_levels()

func fetch_remote_levels() -> void:
	var http = HTTPRequest.new()
	add_child(http)
	http.request_completed.connect(_on_request_completed.bind(http))
	
	var error = http.request(LEVELS_URL)
	if error != OK:
		print("[LevelManager] Erro ao iniciar requisição HTTP para as fases.")

func _on_request_completed(result: int, response_code: int, headers: PackedStringArray, body: PackedByteArray, http_node: HTTPRequest) -> void:
	http_node.queue_free()
	
	if response_code == 200:
		var json = JSON.new()
		var parse_result = json.parse(body.get_string_from_utf8())
		if parse_result == OK:
			level_data = json.get_data()
			print("[LevelManager] Sucesso! Fases atualizadas da nuvem. Total:", level_data.get("total_levels", 0))
			
			# Salva no cache local do dispositivo
			save_local_cache(body)
			
			# Emite sinal para o jogo atualizar a UI ou lógica de fases
			levels_loaded.emit(level_data)
		else:
			print("[LevelManager] Erro ao fazer parse do JSON remoto:", json.get_error_message())
	else:
		print("[LevelManager] Falha ao baixar fases da nuvem. Código HTTP: ", response_code)

func save_local_cache(body: PackedByteArray) -> void:
	var file = FileAccess.open(LOCAL_CACHE_PATH, FileAccess.WRITE)
	if file:
		file.store_buffer(body)
		file.close()

func load_local_cache() -> void:
	if FileAccess.file_exists(LOCAL_CACHE_PATH):
		var file = FileAccess.open(LOCAL_CACHE_PATH, FileAccess.READ)
		if file:
			var content = file.get_as_text()
			file.close()
			var json = JSON.new()
			if json.parse(content) == OK:
				level_data = json.get_data()
				print("[LevelManager] Fases carregadas do cache local (modo offline). Total:", level_data.get("total_levels", 0))
				levels_loaded.emit(level_data)

func get_level(level_id: int) -> Dictionary:
	var levels = level_data.get("levels", [])
	for lvl in levels:
		if lvl.get("id") == level_id:
			return lvl
	return {}
```

---

## 4. Contrato de Dados do `levels.json`

Cada objeto de nível dentro do array `levels` segue estritamente este esquema:

```json
{
  "id": 1,
  "difficulty": "easy",
  "grid_size": [6, 6],
  "dock_slots": 4,
  "passenger_queue": ["brown", "brown", "white", "white"],
  "mystery_indices": [],
  "buses": [
    {
      "id": 1,
      "color": "brown",
      "capacity": 4,
      "x": 1,
      "y": 0,
      "dir": "UP",
      "unlock_after": 0
    }
  ]
}
```

### Descrição dos Campos:
- `id` (int): Identificador único sequencial da fase.
- `difficulty` (string): Nível de dificuldade (`"easy"`, `"medium"`, `"hard"`, `"expert"`).
- `grid_size` (array[int]): Dimensões do estacionamento `[largura, altura]`.
- `dock_slots` (int): Número de vagas de embarque na doca (padrão `4`).
- `passenger_queue` (array[string]): Sequência ordenada de animais/cores que formam a fila de espera.
- `mystery_indices` (array[int]): Índices na fila de passageiros que aparecem como misteriosos (`?`) até chegarem à primeira posição.
- `buses` (array[object]): Lista de ônibus estacionados no grid:
  - `id` (int): ID do ônibus.
  - `color` (string): Cor/espécie do ônibus (`brown`, `white`, `blue`, `yellow`, `pink`).
  - `capacity` (int): Capacidade de passageiros (`4`, `6` ou `8`).
  - `x`, `y` (int): Coordenadas iniciais no grid.
  - `dir` (string): Direção para onde o ônibus aponta/sai (`UP`, `DOWN`, `LEFT`, `RIGHT`).
  - `unlock_after` (int): Quantidade de ônibus que precisam sair antes deste destravar (`0` se começar livre).
