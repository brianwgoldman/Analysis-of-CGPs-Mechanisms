'''
Handles how to perform all of the actual evolution.
'''
import random
import sys
from copy import copy
from util import diff_count
import itertools
from collections import defaultdict


class Individual(object):
    '''
    An individual object used to combine gene fitness with genomes, as
    well methods for manipulating those genomes.
    '''
    def __init__(self, graph_length, input_length, output_length,
                  max_arity, function_list, **_):
        '''
        Create a new individual instance.

        Parameters:

        - ``graph_length``: The number of nodes in the CGP encoded graph.
        - ``input_length``: The number of input variables.
        - ``output_length``: The number of output variables.
        - ``max_arity``: The maximum arity used by any function.
        - ``function_list``: The list of functions a node can use.
        '''
        self.node_step = max_arity + 1
        self.input_length = input_length
        self.graph_length = graph_length
        self.function_list = function_list
        self.output_length = output_length
        self.genes = None
        self.genes = [self.random_gene(index) for index in
                      range(graph_length * self.node_step + output_length)]
        self.determine_active_nodes()
        # If memory problems arise, make this globally shared
        self.scratch = [None] * (graph_length + self.input_length)
        self.fitness = -sys.maxint

    def random_gene(self, index, invalid=None):
        '''
        Determines a random gene value given a gene index.  If optional
        ``invalid`` option is used, the returned value will only be ``invalid``
        if the gene has no other valid values.

        Parameters:

        - ``index``: The gene index who's value is being set.
        - ``invalid``: Value to avoid returning if possible
        '''
        node_number = index // self.node_step
        gene_number = index % self.node_step
        # If the gene is used to specify output locations
        if node_number >= self.graph_length:
            node_number = self.graph_length
            gene_number = -1
        # If the gene controls the function of a node
        if gene_number == 0:
            if len(self.function_list) == 1:
                return self.function_list[0]
            while True:
                choice = random.choice(self.function_list)
                if choice != invalid:
                    return choice
        # If the gene controls a connection / output location
        else:
            if node_number + self.input_length == 1:
                return -1
            while True:
                choice = random.randrange(-self.input_length, node_number)
                if choice != invalid:
                    return choice

    def dag_random_gene(self, index, invalid=None):
        '''
        Determines a random gene value given a gene index of a full DAG.
        If optional ``invalid`` option is used, the returned value
        will only be ``invalid`` if the gene has no other valid values.

        Parameters:

        - ``index``: The gene index who's value is being set.
        - ``invalid``: Value to avoid returning if possible
        '''
        node_number = index // self.node_step
        gene_number = index % self.node_step
        if node_number >= self.graph_length:
            node_number = self.graph_length
            gene_number = -1

        # If it is a function gene
        if gene_number == 0:
            if len(self.function_list) == 1:
                return self.function_list[0]
            while True:
                choice = random.choice(self.function_list)
                if choice != invalid:
                    return choice
        # If you are dealing with output locations or individual initialization
        elif gene_number < 0 or not self.genes:
            if node_number + self.input_length == 1:
                return -1
            while True:
                choice = random.randrange(-self.input_length, node_number)
                if choice != invalid:
                    return choice
        # If you are resetting a connection link on an existing individual
        else:
            return self.valid_reconnect(node_number, invalid)

    def valid_reconnect(self, node_index, invalid=None):
        '''
        When using a DAG individual, find a random connection location that
        does not depend on the current node.

        Parameters:

        - ``node_index``: The index of the node who's connection is being reset
        - ``invalid``: Value to avoid returning if possible
        '''
        # Nodes always depend on themselves and inputs never depend on nodes
        dependent = {node_index: True, invalid: False}
        # Current inputs are not dependent on the mutating node
        for conn in self.connections(node_index):
            dependent[conn] = False
        for index in range(-self.input_length, 0):
            dependent[index] = False

        def is_dependent(current):
            '''
            Internal recursive function to determine if a node index
            is dependent on ``node_index``.  Also updates the dependency
            dictionary.

            Parameters:

            - ``current``: The current working node index to be checked for
              dependency.
            '''
            if current in dependent:
                return dependent[current]
            for conn in self.connections(current):
                if is_dependent(conn):
                    dependent[current] = True
                    return True
            dependent[current] = False
            return False
        # Create the list of all possible connections
        options = range(-self.input_length, self.graph_length)
        for index in range(len(options)):
            # Choose a random untried option and swap it to the next index
            swapdown = random.randrange(index, len(options))
            options[index], options[swapdown] = (options[swapdown],
                                                 options[index])
            option = options[index]
            # Test this option
            if option != invalid and not is_dependent(option):
                return option
        return invalid

    def copy(self):
        '''
        Return a copy of the individual.  Note that individuals are shallow
        copied except for their list of genes.
        '''
        # WARNING individuals are shallow copied except for things added here
        new = copy(self)
        new.genes = list(self.genes)
        return new

    def connections(self, node_index):
        '''
        Return the list of connections that a specified node has.

        Parameters

        - ``node_index``: The index of the node information is being requested
          for.  Note this is different from gene index.
        '''
        node_start = self.node_step * node_index
        return self.genes[node_start + 1: node_start + self.node_step]

    def determine_active_nodes(self):
        '''
        Determines which nodes are currently active and sets self.active
        to the sorted list of active genes.  Automatically called by gene
        manipulating member functions.
        '''
        self.active = set(self.genes[-self.output_length:])

        for node_index in reversed(range(self.graph_length)):
            if node_index in self.active:
                # add all of the connection genes for this node
                self.active.update(self.connections(node_index))
        self.active = sorted([acting for acting in self.active if acting >= 0])

    def dag_determine_active_nodes(self):
        '''
        Determines which nodes are currently active and sets self.active
        to the sorted list of active genes in DAG individuals.
        Automatically called by gene manipulating member functions.
        '''
        depends_on = defaultdict(set)
        feeds_to = defaultdict(set)
        # The output locations start as 'connected'
        connected = self.genes[-self.output_length:]
        added = set(connected)
        # Build a bi-directional dependency tree
        while connected:
            working = connected.pop()
            # Ignore input locations
            if working < 0:
                continue
            for conn in self.connections(working):
                # Record that 'working' takes input from 'conn'
                depends_on[working].add(conn)
                # Record that 'conn' sends its output to 'working'
                feeds_to[conn].add(working)
                if conn not in added:
                    connected.append(conn)
                added.add(conn)
        # find the order in which to evaluate them
        self.active = []
        # All input locations start out addable
        addable = [x for x in range(-self.input_length, 0)]

        while addable:
            working = addable.pop()
            # Find everything that depends on 'working' for input
            for conn in feeds_to[working]:
                # Record that 'conn' is no longer waiting on 'working'
                depends_on[conn].remove(working)
                if len(depends_on[conn]) == 0:
                    addable.append(conn)
                    self.active.append(conn)

    def all_active(self):
        '''
        Function that always makes all nodes in the genome active.  Useful
        when the fitness function analyzes nodes directly when combined with
        Single mutation.
        '''
        self.active = range(self.graph_length)

    def evaluate(self, inputs):
        '''
        Given a list of inputs, return a list of outputs from executing
        this individual.

        Parameters:

        - ``inputs``: The list of input values for the individual to process.
        '''
        # Start by loading the input values into scratch
        # NOTE: Input locations are given as negative values
        self.scratch[-len(inputs):] = inputs[::-1]
        # Loop through the active genes in order
        for node_index in self.active:
            function = self.genes[node_index * self.node_step]
            args = [self.scratch[con] for con in self.connections(node_index)]
            # Apply the function to the inputs from scratch, saving results
            # back to the scratch
            self.scratch[node_index] = function(*args)
        # Extract outputs from the scratch space
        return [self.scratch[output]
                for output in self.genes[-self.output_length:]]

    def mutate(self, mutation_rate):
        '''
        Return a mutated version of this individual using the specified
        mutation rate.

        Parameters:

        - ``mutation_rate``: The probability that a specific gene will mutate.
        '''
        mutant = self.copy()
        for index in range(len(mutant.genes)):
            if random.random() < mutation_rate:
                mutant.genes[index] = mutant.random_gene(index,
                                                         mutant.genes[index])
        # Have the mutant recalculate its active genes
        mutant.determine_active_nodes()
        return mutant

    def one_active_mutation(self, _):
        '''
        Return a mutated version of this individual using the ``Single``
        mutation method.
        '''
        mutant = self.copy()
        while True:
            # Choose an index at random
            index = random.randrange(len(mutant.genes))
            # Get a new value for that gene
            newval = mutant.random_gene(index)
            # If that value is different than the current value
            if newval != mutant.genes[index]:
                mutant.genes[index] = newval
                # Determine if that gene was part of an active node
                node_number = index // self.node_step
                if (node_number >= self.graph_length or
                    node_number in self.active):
                    break
        # Have the mutant recalculate its active genes
        mutant.determine_active_nodes()
        return mutant

    def reorder(self):
        '''
        Return an individual who's genes have been reordered randomly without
        changing any of the actual connection information.
        '''
        # Build a list of dependencies
        depends_on = defaultdict(set)
        feeds_to = defaultdict(set)
        for node_index in range(self.graph_length):
            for conn in self.connections(node_index):
                # Record that 'node_index' takes input from 'conn'
                depends_on[node_index].add(conn)
                # Record that 'conn' sends its output to 'node_index'
                feeds_to[conn].add(node_index)
        # Create a dictionary storing how to translate location information
        new_order = {i: i for i in range(-self.input_length, 0)}
        # Input locations start as addable
        addable = new_order.keys()
        counter = 0
        while addable:
            # Choose a node at random who's dependencies have already been met
            working = random.choice(addable)
            addable.remove(working)
            # If 'working' is not an input location
            if working >= 0:
                # Assign this node to the next available index
                new_order[working] = counter
                counter += 1
            # Update all dependencies now that this node has been added
            for to_add in feeds_to[working]:
                # Mark 'to_add' as having its requirement on 'working' complete
                depends_on[to_add].remove(working)
                if len(depends_on[to_add]) == 0:
                    addable.append(to_add)

        # Create the new individual using the new ordering
        mutant = self.copy()
        for node_index in range(self.graph_length):
            # Find the new starting location in the mutant for this node
            start = new_order[node_index] * self.node_step
            # Move over the function gene
            mutant.genes[start] = self.genes[node_index * self.node_step]
            # Translate connection genes to have new order information
            connections = [new_order[conn]
                           for conn in self.connections(node_index)]
            # Move over the connection genes
            mutant.genes[start + 1:start + self.node_step] = connections
        length = len(self.genes)
        # Update the output locations
        for index in range(length - self.output_length, length):
            mutant.genes[index] = new_order[self.genes[index]]
        # Have the mutant recalculate its active genes
        mutant.determine_active_nodes()
        return mutant

    def asym_phenotypic_difference(self, other):
        '''
        Determine how many genes would have to be mutated in order to make
        the ``other`` individual phenotypically identical to ``self``.

        Parameters:

        - ``other``: The individual to compare with.
        '''
        # Count the differences in the output locations
        count = diff_count(self.genes[-self.output_length:],
                           other.genes[-self.output_length:])
        # For each active node
        for node_index in self.active:
            index = node_index * self.node_step
            # Count the number of different connection genes
            count += diff_count(self.connections(node_index),
                                other.connections(node_index))
            # Include differences in the function gene
            count += (self.genes[index] !=
                      other.genes[index])
        return count

    def show_active(self):
        '''
        Prints the active portions of the individual in a somewhat readable
        way.
        '''
        for node_index in self.active:
            node_start = self.node_step * node_index
            print node_index, self.genes[node_start],
            print self.connections(node_index)
        print self.genes[-self.output_length:]

    def get_fitness(self):
        '''
        Returns the fitness of the individual.
        '''
        return self.fitness

    def more_active(self):
        '''
        Returns a tuple of (fitness, # of active nodes).  Can be used to
        override get_fitness to cause selection to favor longer individuals.
        '''
        return (self.fitness, len(self.active))

    def less_active(self):
        '''
        Returns a tuple of (fitness, -# of active nodes).  Can be used to
        override get_fitness to cause selection to favor shorter individuals.
        '''
        return (self.fitness, -len(self.active))

    def __lt__(self, other):
        '''
        Returns the result of self.get_fitness() < other.get_fitness().
        '''
        return self.get_fitness() < other.get_fitness()

    def __le__(self, other):
        '''
        Returns the result of self.get_fitness() <= other.get_fitness().
        '''
        return self.get_fitness() <= other.get_fitness()


def generate(config, output, frequencies):
    '''
    An ``Individual`` generator that will yield a never ending supply of
    ``Individual`` objects that need to have their fitness set before the
    next ``Individual`` can be yielded.

    Parameters:

    - ``config``: A dictionary containing all configuration information
      required to generate initial individuals.  Should include values
      for:

      - All configuration information required to initialize an Individual.
      - ``dag``: If DAG based individuals should be used.
      - ``reorder``: If the parent should be reordered before making offspring.
      - ``mutation_rate``: The probably to use for mutation.
      - ``off_size``: The number of offspring to produce per generation.
      - ``output_length``: The number of output variables.
      - ``max_arity``: The maximum arity used by any function.
      - ``speed``: String specifying the way to handle duplicate
        individual creation, either ``normal'', ``skip'', ``accumulate``, or
        ``single``.
      - ``active_push``: Determines if fitness should break ties depending on
        number of active nodes.
        Valid settings are ``none``, ``more``, or ``less``.
      - ``problem``: The problem these individuals are solving.  Used on in
        the case where problems require unusual individual modification.
    - ``output``: Dictionary used to return information about evolution, will
      send out:

      - ``skipped``: The number of individuals skipped by ``Skip``.
      - ``estimated``: The estimated number of individuals that are skippable.
    - ``frequencies``:  Dictionary used to return information about how often
      individuals of different lengths are evolved.
    '''
    output['skipped'] = 0
    output['estimated'] = 0
    if config['dag']:
        # Override base functions with dag versions
        Individual.determine_active_nodes = \
        Individual.dag_determine_active_nodes
        Individual.random_gene = \
        Individual.dag_random_gene
    if config['speed'] == 'single':
        # Override normal mutation with Single
        Individual.mutate = Individual.one_active_mutation
    if config['active_push'] == 'more':
        # Override normal fitness with bias toward more active nodes
        Individual.get_fitness = Individual.more_active
    elif config['active_push'] == 'less':
        # Override normal fitness with bias toward less active nodes
        Individual.get_fitness = Individual.less_active
    if config['problem'] == 'Flat':
        # Override normal method for determining active genes
        Individual.determine_active_nodes = Individual.all_active
    parent = Individual(**config)
    # Evaluate initial individual
    yield parent
    while True:
        if config['reorder']:
            # Replace the parent with a reordered version of itself
            parent = parent.reorder()
        # Create mutant offspring
        mutants = [parent.mutate(config['mutation_rate'])
                   for _ in range(config['off_size'])]
        # Determine how many active genes the parent has
        active = config['output_length'] + (len(parent.active) *
                                            (config['max_arity'] + 1))
        for index, mutant in enumerate(mutants):
            output['estimated'] += (1 - config['mutation_rate']) ** active
            prev = mutant
            if config['speed'] not in ['normal', 'single']:
                change = parent.asym_phenotypic_difference(mutant)
                if change == 0:
                    output['skipped'] += 1
                    if config['speed'] == 'skip':
                        continue
                    if config['speed'] == 'accumulate':
                        while change == 0:
                            # As long as there have been no changes,
                            # keep mutating
                            prev = mutant
                            mutant = prev.mutate(config['mutation_rate'])
                            change = parent.asym_phenotypic_difference(mutant)
            if 'frequency_results' in config:
                # Records the length of the generated individual
                frequencies[len(mutant.active)] += 1
            # Send the offspring out to be evaluated
            yield mutant
            if config['speed'] == 'accumulate':
                # If the mutant is strickly worse, use the last equivalent
                mutants[index] = prev if mutant < parent else mutant
        best_child = max(mutants)
        if parent <= best_child:
            parent = best_child


def multi_indepenedent(config, output, frequencies):
    '''
    Allows for multiple parallel independent populations to be evolved
    at the same time.  Will generate one individual from each population
    before repeating a population.

    Parameters:

    - ``config``: A dictionary containing all of the configuration information
      required to generate multiple populations worth of individuals.  Should
      include values for:

      - All configuration information required by ``generate``.
      - ``pop_size``: The number of parallel populations to use.
    - ``output``:  Used to return information about evolution.  Shared by all
      parallel populations.  Will contain all information output by
      ``generate``.
    - ``frequencies``:  Dictionary used to return information about how often
      individuals of different lengths are evolved.  Shared by all parallel
      populations.  Will contain all information output by ``generate``.
    '''
    collective = itertools.izip(*[generate(config, output, frequencies)
                                  for _ in range(config['pop_size'])])
    for next_iterations in collective:
        for next_iteration in next_iterations:
            yield next_iteration
