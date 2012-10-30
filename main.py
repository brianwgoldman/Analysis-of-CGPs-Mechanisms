'''
This module is intended to duplicate the 'main()' function found in other
languages such as C++ and Java.  In order to run an experiment, this module
should be passes to your interpreter.  In the interest of speed and consistency
we suggest that PyPy 1.9.0 be used to run this code, although
Python 2.7 should be able to handle it correctly.

To see a full description of this modules command line arguments, run
````pypy main.py -h````.

Provided with this code should be the ``cfg`` folder which contains some
configuration files useful for running experiments.  These files can be passed
to main along with other configuration information in order to recreate
the experiments performed in the Reducing Wasted Evaluations in Cartesian
Genetic Programming publication.  For example, the following command runs a
the ``Accumulate`` mutation method on the Parity problem using seed number
13 with 3000 nodes in the graph and a mutation rate of 0.01 with verbose
output turned on, outputting the results to output/test_run.dat.

``pypy main.py cfg/once.cfg cfg/parity.cfg -g 3000 -m 0.01
-seed 13 -s accumulate -v -o output/test_run.dat``

For any support questions email brianwgoldman@acm.org.
'''

from evolution import Individual, multi_indepenedent
import problems
import util


def one_run(evaluator, config):
    '''
    Performs a single run of the given configuration.  Returns a dictionary
    containing results.

    Parameters:

    - ``evaluator``: An object with the function get_fitness that takes an
      individual and returns its fitness value
    - ``config``: A dictionary containing all of the configuration information
      required to perform a experimental run, including:

      - All information required to initialize an individual.
      - All information required to run ``evolution.multi_independent``.
      - ``verbose``: Boolean value for if extra runtime information should
        be displayed.
      - ``max_evals``: The maximum number of evaluations allowed before
        termination.
      - ``max_fitness``: The fitness required to cause a "successful"
        termination.
    '''
    best = Individual(**config)
    last_improved = -1
    output = {}
    for evals, individual in enumerate(multi_indepenedent(config, output)):
        individual.fitness = evaluator.get_fitness(individual)
        if best < individual:
            best = individual
            last_improved = evals
            if config['verbose']:
                print '\t', last_improved, best.fitness, len(best.active)
        if (evals >= config['max_evals'] or
            best.fitness >= config['max_fitness']):
            break
    if config['verbose']:
        print "Best Found"
        best.show_active()
    output.update({'fitness': best.fitness, 'evals': evals,
                   'success': best.fitness >= config['max_fitness'],
                   'phenotype': len(best.active),
                   'normal': output['skipped'] + evals})
    return output


def all_runs(config):
    '''
    Perform all of the requested runs on a given problem.  Returns a list of
    the dictionaries returned by ``one_run``.  Will give results for all
    completed runs if a keyboard interrupt is received.

    Parameters:

    - ``config``: Dictionary containing all configuration information required
      to perform all of the necessary runs of the experiment.  Should contain
      values for:

      - All configuration information needed by ``one_run``
      - ``problem``: The name of which problem from the ``problem`` module to
        run experiments on.
      - ``runs``: How many runs to perform
    '''
    problem_function = problems.__dict__[config['problem']]
    evaluator = problems.Problem(problem_function, config)
    config['function_list'] = problem_function.operators
    config['max_arity'] = problem_function.max_arity
    results = []
    try:
        for run in range(config['runs']):
            print "Starting Run", run + 1
            result = one_run(evaluator, config)
            print result
            results.append(result)
    except KeyboardInterrupt:
        print "Interrupted"
    return results


def combine_results(results):
    '''
    Given a list of result dictionaries, return analysis information such as
    the median values of each statistic as well as the median absolute
    deviation.

    Parameters:

    - ``results``: A list of dictionaries containing similar key values.
    '''
    combined = {}
    # Collect the successful runs
    successful = [result for result in results if result['success']]
    # Combine like keys across all runs
    for result in results:
        for key, value in result.iteritems():
            try:
                combined[key].append(value)
            except KeyError:
                combined[key] = [value]
    # Analyze the values for each key
    for key, value in combined.items():
        combined[key] = util.median_deviation(value)
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
    parser.add_argument('-m', dest='mutation_rate', type=float,
                        help='Use the specified mutation rate.')
    parser.add_argument('-p', dest='problem', type=str,
                        help='Use the specified problem.')
    parser.add_argument('-pop_size', dest='pop_size', type=int,
                        help='Use the specified population size.')
    parser.add_argument('-seed', dest='seed', type=int,
                        help='Use the specified random seed used')
    parser.add_argument('-s', dest='speed', type=str,
                        help='Specifies if evolution should should avoid' +
                        ' duplicated evaluations.  Valid settings are: ' +
                        'normal, skip, accumulate, single')
    parser.add_argument('-r', dest='reorder', action='store_true',
                        help='Include this flag to have mutant reordering')
    parser.add_argument('-dag', dest='dag', action='store_true',
                        help='Include this flag for full dag representation')
    parser.add_argument('-c', dest='output_config', type=str,
                        help='Outputs a single configuration file containing' +
                        ' the entire configuration used in this run')
    parser.add_argument('-v', dest='verbose', action='store_true',
                        help='Include this flag to increase periodic output')

    parser.add_argument('-o', dest='output_results', type=str,
                        help='Specify a file to output the results.')

    parser.add_argument('-profile', dest='profile', action='store_true',
                        help='Include this flag to run a profiler')

    args = parser.parse_args()
    config = util.load_configurations(args.configs)
    config['verbose'] = args.verbose
    config['reorder'] = args.reorder
    config['dag'] = args.dag

    if args.seed != None:
        config['seed'] = args.seed
    elif 'seed' not in config:
        config['seed'] = random.randint(0, sys.maxint)
    random.seed(config['seed'])

    if args.graph_length != None:
        config['graph_length'] = args.graph_length

    if args.mutation_rate != None:
        config['mutation_rate'] = args.mutation_rate

    if args.problem != None:
        config['problem'] = args.problem

    if args.pop_size != None:
        config['pop_size'] = args.pop_size

    if args.speed != None:
        config['speed'] = args.speed

    if args.profile:
        # When profiling, just run the configuration
        import cProfile
        cProfile.run("all_runs(config)", sort=2)
        sys.exit()

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
