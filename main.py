import evolution
import problems
import util


def one_run(evaluator, config):
    best = evolution.Individual(**config)
    last_improved = -1
    for evals, individual in enumerate(evolution.generate(config)):
        individual.fitness = evaluator.get_fitness(individual)
        if best < individual:
            best = individual
            last_improved = evals
            if config['verbose']:
                print '\t', last_improved, best.fitness
        if (evals >= config['max_evals'] or
            best.fitness >= config['max_fitness']):
            break
    return {'fitness': best.fitness, 'evals': last_improved,
            'success': best.fitness >= config['max_fitness']}


def all_runs(config):
    problem_function = problems.__dict__[config['problem']]
    evaluator = problems.Problem(problem_function, config)
    config['function_list'] = problem_function.operators
    config['max_arity'] = problem_function.max_arity
    results = []
    for run in range(config['runs']):
        if config['verbose']:
            print "Starting Run", run
        results.append(one_run(evaluator, config))
    return results


def combine_results(results):
    combined = {}
    # Only gather results from successful runs
    successful = [result for result in results if result['success']]
    for result in successful:
        for key, value in result.iteritems():
            try:
                combined[key].append(value)
            except KeyError:
                combined[key] = [value]
    for key, value in combined.items():
        combined[key] = util.meanstd(value)
    try:
        combined['success'] = len(successful) / float(len(results)), 0
    except ZeroDivisionError:
        combined['success'] = 0, 0
    return combined

if __name__ == '__main__':
    import argparse
    import random
    import sys

    description = 'Cartesian Genetic Programming.  In Python!'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('configs', metavar='Configuration Files',
                        type=str, nargs='+',
                        help='Zero or more json formatted files containing' +
                            ' configuration information')

    parser.add_argument('-g', dest='graph_length', type=int,
                        help='The number of nodes in the CGP graph')
    parser.add_argument('-r', dest='mutation_rate', type=float,
                        help='Use the specified mutation rate.')
    parser.add_argument('-p', dest='problem', type=str,
                        help='Use the specified problem.')
    parser.add_argument('-s', dest='speed', type=str,
                        help='Specifies if evolution should should avoid' +
                        ' duplicated evaluations.  Valid settings are: ' +
                        'normal, no_reeval, mutate_until_change')
    parser.add_argument('-c', dest='output_config', type=str,
                        help='Outputs a single configuration file containing' +
                        ' the entire configuration used in this run')
    parser.add_argument('-v', dest='verbose', action='store_true',
                        help='Include this flag to increase periodic output')

    parser.add_argument('-o', dest='output_results', type=str,
                        help='Specify a file to output the results.')

    args = parser.parse_args()
    config = util.load_configurations(args.configs)
    config['verbose'] = args.verbose

    if 'seed' not in config:
        config['seed'] = random.randint(0, sys.maxint)
    random.seed(config['seed'])

    if args.graph_length != None:
        config['graph_length'] = args.graph_length

    if args.mutation_rate != None:
        config['mutation_rate'] = args.mutation_rate

    if args.problem != None:
        config['problem'] = args.problem

    try:
        raw_results = all_runs(config)
        combined = combine_results(raw_results).items()
        print sorted(combined)
        if args.output_results != None:
            util.save_list(args.output_results, [combined] + raw_results)
        if args.output_config != None:
            util.save_configuration(args.output_config, config)
    except KeyError as e:
        print 'You must include a configuration value for', e.args[0]
