from ortools.linear_solver import pywraplp
from toposort import toposort_flatten

def leituraDeArquivo(nomeDoArquivo):
	arquivo = open(nomeDoArquivo)
	lines =  arquivo.readlines()

	numeroDeTarefas = int(lines[0])
	diaDaEntrega = int(lines[1])
	multa = int(lines[2])
	numeroDePrecedencias = int(lines[3])

	precedencia = [[0 for j in range(numeroDeTarefas)] for i in range(numeroDeTarefas)]
	precedenciaDict  = {}
	duracao = [[0 for j in range(3)] for i in range(numeroDeTarefas)]
	custo = [[0 for j in range(3)] for i in range(numeroDeTarefas)]

	for i in lines[5 : 5 + numeroDePrecedencias]:
		informacao = i.split(' ')
		precedencia[int(informacao[0]) - 1][int(informacao[1]) - 1] = 1

		if (int(informacao[1]) - 1) not in precedenciaDict.keys():
			precedenciaDict[int(informacao[1]) - 1] = {int(informacao[0]) - 1}
		else:
			print(precedenciaDict.keys())
			precedenciaDict[int(informacao[1]) - 1].update({int(informacao[0]) - 1})
	
	for i in lines[(3 + 3 + numeroDePrecedencias):]:
		informacao = i.split(' ')
		for j in range(3):
			duracao[int(informacao[0])-1][j] = int(informacao[j+1])
		for j in range(3):
			custo[int(informacao[0])-1][j] = int(informacao[j+4])

	return numeroDeTarefas, diaDaEntrega, multa, duracao, custo, precedencia,precedenciaDict


def main():
	numeroDeTarefas, diaDaEntrega, multa, duracao, custo, precedencia,precedenciaDict = leituraDeArquivo('instancia.txt')
	#print(numeroDeTarefas, diaDaEntrega, multa, duracao, custo, precedencia, precedenciaDict)

	solver = pywraplp.Solver.CreateSolver('GLOP')

	#adiciona variável
	x = {}
	for i in range(numeroDeTarefas):
		for j in range(3):
				x[i,j] = solver.IntVar(0, 1, 'x' + str(i) + str(j))

	#adiciona restrição
	for i in range(numeroDeTarefas):
		somatorio1 = solver.Sum([x[i,j] for j in range(3)])
		solver.Add(somatorio1 == 1)

	#adiciona função objetivo
	objectivesCusto = []
	objectivesDuracao = []
	for i in range(numeroDeTarefas):
		for j in range(3):
			objectivesCusto.append(x[i,j] * custo[i][j])
			objectivesDuracao.append(x[i,j] * duracao[i][j])


	solver.Minimize(solver.Sum(objectivesCusto) + ((solver.Sum(objectivesDuracao)) - diaDaEntrega)*multa)

	#exporta o modelo
	modelo = solver.ExportModelAsLpFormat(False)
	arquivo = open("modelo.lp", "w")
	arquivo.write(modelo)
	arquivo.close()
	#print(modelo)

	#resolve
	status = solver.Solve()

	ordemDasTarefas = toposort_flatten(precedenciaDict)

	tempoTotal = 0
	custoTotal = 0

	print('Status: ', status, end = " ")
	print("\nObj: " , solver.Objective().Value())
	print('Planejamento:')
	for i in range(numeroDeTarefas):
		for j in range(3):
			if x[i,j].solution_value() != 0:
				print("tarefa ", ordemDasTarefas[i] + 1, " no modo ", j, " com custo ", custo[i][j], " comecando no tempo ", tempoTotal, " e terminando no tempo ", tempoTotal + duracao[i][j] - 1)
				tempoTotal += duracao[i][j]
				custoTotal += custo[i][j]
		print("\n")	

	print("\nCusto adicionais das tarefas: ", custoTotal, end = ' ')
	print("\nCusto de multa: ", ((tempoTotal - diaDaEntrega) * multa), end = ' ')
	print("\nCusto total: ", ((tempoTotal - diaDaEntrega) * multa) + custoTotal, end = ' ')
	print("\nTempo total: ", tempoTotal)



if __name__ == '__main__':
	main()