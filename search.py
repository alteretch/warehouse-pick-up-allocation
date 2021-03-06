from actions import Actions
import util
import heapq


class Node:
    def __init__(self, pos):
        """
        Initialize node
        :param pos: node position
        """
        self.pos = pos
        self.g = 100000
        self.f = 100000
        self.prev = self

    def set_travel_cost(self, cost):
        """
        Set the travel cost
        :param cost:
        """
        self.g = cost

    def set_total_cost(self, cost):
        """
        Set the total cost
        :param cost:
        """
        self.f = cost

    def set_previous_node(self, node):
        """
        Set the previous node
        :param node:
        """
        self.prev = node

    def get_travel_cost(self):
        """
        Return the travel cost so far
        :return: travel_cost
        """
        return self.g

    def get_total_cost(self):
        """
        Return the total cost so far
        :return: total_cost
        """
        return self.f

    def get_previous_node(self):
        """
        Return the previous node of this node
        :return: node
        """
        return self.prev


class PathFind:
    def __init__(self, robot):
        """
        Initialize the PathFind object
        :param robot:
        """
        self.robot = robot
        self.start = Node(self.robot.pos)
        self.current = self.start
        if self.robot.task:
            self.goals = [Node(self.robot.task[0].pos)]
        else:
            self.goals = []
        self.toNeighbours = False

    def perform_a_star_search(self):
        """
        A regular A* graph search that returns the absolute path and relative path (in terms of directions)
        :return: absPath, dirPath
        """
        closed_set = []

        # The set of currently discovered nodes that are not evaluated yet.
        # Initially, only the start node is known.
        open_set = [self.start]

        self.start.set_travel_cost(0)
        self.start.set_total_cost(self.get_heuristic_cost(self.start))

        while len(open_set) > 0:
            self.current = self.get_min_cost_node(open_set)
            open_set.remove(self.current)
            closed_set.append(self.current)

            for goal in self.goals:
                if self.current.pos == goal.pos:
                    return self.reconstruct_path(self.current)

            successors = self.get_robot_successors(self.current.pos)

            for node in successors:
                if self.check_node_in_set(node, closed_set):
                    continue

                if not self.check_node_in_set(node, open_set):
                    open_set.append(node)

                one_step_cost=self.robot.world.gridCost.get(tuple(self.current.pos+node.pos))
                tentative_travel_cost = self.current.get_travel_cost() + one_step_cost
                if tentative_travel_cost >= node.get_travel_cost():
                    continue

                node.set_previous_node(self.current)
                node.set_travel_cost(tentative_travel_cost)
                node.set_total_cost(node.get_travel_cost() + self.get_heuristic_cost(node))

    def reconstruct_path(self, current):
        """
        Reconstruct the absolute and directional path based on the results of A* search.
        :param current:
        :return: abs_path, dir_path
        """
        path = [current.pos]
        dir_path = []
        while current.get_previous_node().pos != current.pos:
            current = current.get_previous_node()
            path.insert(0, current.pos)

        for i in range(len(path) - 1):
            dir_path.append([path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]])

        return path, dir_path

    def check_node_in_set(self, node, target_set):
        """
        Returns whether the set contains a node with identical position with the parameter node.
        :param node:
        :param target_set:
        :return: boolean
        """
        for setNode in target_set:
            if node.pos == setNode.pos:
                return True
        return False

    def get_robot_successors(self, pos):
        """
        Returns the successor positions of the robot at pos
        :param pos:
        :return: (list)position
        """
        possible = Actions.get_possible_actions(pos, self.robot.world)
        if possible == [Actions.STOP]:
            possible = Actions.get_possible_actions(pos, self.robot.world)
        successor = []
        for direction in possible:
            x = pos[0] + direction[0]
            y = pos[1] + direction[1]
            successor.append(Node([x, y]))
        return successor

    def get_min_cost_node(self, target_set):
        """
        Returns the node in target_set with the lowest cost
        :param target_set:
        :return: min_node
        """
        min_val = 1000000
        min_node = None
        for node in target_set:
            if node.get_total_cost() < min_val:
                min_val = node.get_total_cost()
                min_node = node
        return min_node

    def get_heuristic_cost(self, node):
        """
        Calculate the heuristic cost of a particular node
        :param node:
        :return: heuristic_cost
        """
        min_dist = 1000000
        for goal in self.goals:
            dist = util.calculate_manhattan_distance(node.pos, goal.pos)
            if dist < min_dist:
                min_dist = dist
        return min_dist


"""
    ------------------------------------------------------------------------------
    |                                                                            |
    |   The codes below are mainly used for Clarke and Wright savings algorithm  |
    |                                                                            |
    ------------------------------------------------------------------------------
"""


class Graph:
    """
    Class Graph based on the graph theory
    """

    def __init__(self, nodes):
        self.__vertices = []
        self.__graph_group = []  # (list)[[group 0],[group 1]...] elements linked together are put in the same group
        for i in range(nodes):
            self.__vertices.append(i)
            self.__graph_group.append([i])

    def location(self, vert):
        """
        Find out where the vert is in the self.__graph_group
        :param vert
        :return: i,j i_th group, j_th element
        """
        i = 0
        for group in self.__graph_group:
            j = 0
            for item in group:
                if vert == item:
                    return i, j
                j += 1
            i += 1

    def is_head(self, loc):
        """
        Whether the vert is the 1st element in the group
        :param loc: from self.location()
        :return: boolean
        """
        (i, j) = loc
        if j == 0:
            return True
        else:
            return False

    def is_tail(self, loc):
        """
        Whether the vert is the last element in the group
        :param loc: from self.location()
        :return: boolean
        """
        (i, j) = loc
        if j == len(self.__graph_group[i]) - 1:
            return True
        else:
            return False

    def set_edge(self, vert1, vert2):
        """
        Set the edge of two vertex, updating the self.__graph_group
        :param vert1:
        :param vert2:
        :return: True for success, False for fail
        """
        loc1 = self.location(vert1)
        loc2 = self.location(vert2)
        if loc1[0] == loc2[0]:
            return False
        if self.is_tail(loc1):
            if self.is_head(loc2):
                self.__graph_group[loc1[0]] = self.__graph_group[loc1[0]] + self.__graph_group[loc2[0]]
                self.__graph_group.pop(loc2[0])
                return True
            elif self.is_tail(loc2):
                self.__graph_group[loc1[0]] = self.__graph_group[loc1[0]] + self.__graph_group[loc2[0]][::-1]
                self.__graph_group.pop(loc2[0])
                return True
        elif self.is_head(loc1):
            if self.is_head(loc2):
                self.__graph_group[loc1[0]] = self.__graph_group[loc2[0]][::-1] + self.__graph_group[loc1[0]]
                self.__graph_group.pop(loc2[0])
                return True
            elif self.is_tail(loc2):
                self.__graph_group[loc1[0]] = self.__graph_group[loc2[0]] + self.__graph_group[loc1[0]]
                self.__graph_group.pop(loc2[0])
                return True

    def load(self, vert):
        """

        :param vert:
        :return: (int) amount of the tasks
        """
        loc = self.location(vert)
        load = len(self.__graph_group[loc[0]])
        return load

    def gen_link(self):
        """

        :return: (list)
        """
        if self.__graph_group:
            link = max(self.__graph_group, key=lambda x: len(x))
            return link
        return None

    def try_gen_link(self):
        """

        :return: (list)link or None
        """
        for link in self.__graph_group:
            if len(link) == util.ROBOT_CAPACITY:
                return link
        return None


class PriorityQueue:
    """
    Class PriorityQueue used for A* algorithm
    """

    def __init__(self):
        self.element = []

    def empty(self):
        return len(self.element) == 0

    def put(self, item, priority):
        heapq.heappush(self.element, (priority, item))

    def get(self):
        return heapq.heappop(self.element)[1]


def a_star_planning(world, start, goal):
    """
    Calculate distance cost of each point and show from which parent point the current point comes from.
    This is an exhaustive search that generates a table for every node and should only be used for the saving table
    because of the longer search time than regular A* search.
    :param world:
    :param start:
    :param goal:
    :return: (dict) (came_from, cost_so_far)
    """
    start = tuple(start)
    goal = tuple(goal)
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = dict()
    came_from[start] = None
    cost_so_far[start] = 0
    current = []

    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            break

        for next_pos in world.neighbors(current):
            new_cost = cost_so_far[current] + 1
            if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                cost_so_far[next_pos] = new_cost
                priority = new_cost + util.calculate_manhattan_distance(goal, next_pos)
                frontier.put(next_pos, priority)
                came_from[next_pos] = current

    return came_from, cost_so_far[current]


def saving_dist_table(world):
    """
    Calculate distance cost saving between each two task positions
    and sort the saving decreasingly. Used in Clarke and Wright Algorithm only.
    :param world:
    :return: (list)saving_table
    """
    task_pos_list = []
    task_num = int(util.ROBOT_CAPACITY * util.TEMPORAL_PRIORITY_FACTOR)
    for item in world.taskCache[:task_num]:
        task_pos_list.append(item.pos)
    task_num = len(task_pos_list)
    distance_table = {}
    for index, task in enumerate(task_pos_list):
        cost = a_star_planning(world, util.START_POINT, task)[1]
        distance_table[(-1, index)] = cost
    for index1 in range(0, len(task_pos_list) - 1):
        for index2 in range(index1 + 1, len(task_pos_list)):
            cost = a_star_planning(world, task_pos_list[index1], task_pos_list[index2])[1]
            distance_table[(index1, index2)] = cost
    saving_table = {}
    for (task1, task2) in distance_table:
        if task1 != -1:
            saving_table[(task1, task2)] = \
                distance_table[(-1, task1)] + distance_table[(-1, task2)] - distance_table[(task1, task2)]
    saving_table = sorted(saving_table.items(), key=lambda x: x[1], reverse=True)
    return saving_table, task_num


def sort_task(world):
    """
    Generate separated sequences according to the saving_table.
    :param world:
    :return:(list)[[task00,task01,...],[task10,task11,...],...]
    """
    (saving_table, task_num) = saving_dist_table(world)
    task_index_list = range(task_num)
    g = Graph(len(task_index_list))
    for item in saving_table:
        (task1, task2) = item[0]
        if len(task_index_list) == 0:
            break
        if g.try_gen_link():
            return g.try_gen_link()
        if g.load(task1) + g.load(task2) <= util.ROBOT_CAPACITY:
            if g.set_edge(task1, task2):
                try:
                    task_index_list.remove(task1)
                except ValueError:
                    pass
                try:
                    task_index_list.remove(task2)
                except ValueError:
                    pass
    return g.gen_link()
