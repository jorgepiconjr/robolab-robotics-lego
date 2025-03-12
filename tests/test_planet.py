#!/usr/bin/env python3

from platform import node
import unittest
from typing import Tuple, Dict, Optional, List
from planet import Direction, Planet, Weight


class ExampleTestPlanet(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        +--+
        |  |
        +-0,3------+
           |       |
          0,2-----2,2 (target)
           |      /
        +-0,1    /
        |  |    /
        +-0,0-1,0
           |
        (start)

        """
        # Initialize your data structure here
        self.planet = Planet()
        self.planet.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.SOUTH), 1)
        self.planet.add_path(((0, 1), Direction.WEST), ((0, 0), Direction.WEST), 1)

    @unittest.skip('Example test, should not count in final test results')
    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """
        self.assertIsNone(self.planet.shortest_path((0, 0), (1, 2)))


class TestRoboLabPlanet(unittest.TestCase):
    def setUp(self):
        # Initialize your data structure here
        # Hinweis: wenn eine Himmelrichtung für den selben Knoten mehrmals vorhanden ist, dann wird der Eintrag genutzt
        self.planet = Planet()
        self.planet.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.WEST), 1)
        self.planet.add_path(((0, 1), Direction.WEST), ((0, 2), Direction.WEST), 2)
        self.planet.add_path(((0, 2), Direction.WEST), ((0, 3), Direction.WEST), 2)

        self.planet_empty = Planet()
        
        self.planet_with_loop = Planet()
        self.planet_with_loop.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.WEST), 1)
        self.planet_with_loop.add_path(((0, 1), Direction.NORTH), ((0, 0), Direction.WEST), 1)
        self.planet_with_loop.add_path(((0, 1), Direction.WEST), ((0, 2), Direction.WEST), 2)
        self.planet_with_loop.add_path(((0, 2), Direction.WEST), ((0, 3), Direction.WEST), 1)

        self.planet_triangle = Planet()
        self.planet_triangle.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.WEST), 1)
        # Es ist schlauer von (0,0) zu (0,2) zu gehen
        self.planet_triangle.add_path(((0, 0), Direction.WEST), ((0, 2), Direction.WEST), 2)
        self.planet_triangle.add_path(((0, 1), Direction.WEST), ((0, 2), Direction.WEST), 2)
        self.planet_triangle.add_path(((0, 2), Direction.WEST), ((0, 3), Direction.WEST), 1)

        self.planet_equal_paths = Planet()
        self.planet_equal_paths.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.WEST), 1)
        self.planet_equal_paths.add_path(((0, 0), Direction.SOUTH), ((0, 1), Direction.WEST), 1)
        self.planet_equal_paths.add_path(((0, 1), Direction.WEST), ((0, 2), Direction.WEST), 2)
        self.planet_equal_paths.add_path(((0, 2), Direction.WEST), ((0, 3), Direction.WEST), 1)

        self.planet_big_loop = Planet()
        self.planet_big_loop.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.WEST), 1)
        self.planet_big_loop.add_path(((0, 0), Direction.EAST), ((0, 0), Direction.SOUTH), 1)
        self.planet_big_loop.add_path(((0, 1), Direction.NORTH), ((0, 0), Direction.WEST), 1)
        self.planet_big_loop.add_path(((0, 1), Direction.WEST), ((0, 2), Direction.WEST), 2)
        self.planet_big_loop.add_path(((0, 2), Direction.WEST), ((0, 3), Direction.WEST), 1)

        self.planet_minus_paths = Planet()
        self.planet_minus_paths.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.WEST), 1)
        self.planet_minus_paths.add_path(((0, 1), Direction.WEST), ((0, 2), Direction.WEST), 2)
        self.planet_minus_paths.add_path(((0, 2), Direction.WEST), ((0, 3), Direction.WEST), -1)

        self.planet_wakanda = Planet()
        self.planet_wakanda.add_path(((68, 421),Direction.NORTH),((68, 422), Direction.SOUTH), 1)
        self.planet_wakanda.add_path(((68, 421),Direction.EAST),((68, 421), Direction.EAST), -1)
        self.planet_wakanda.add_path(((69, 421),Direction.WEST),((69, 421), Direction.WEST), -1)
        self.planet_wakanda.add_path(((69, 421),Direction.SOUTH),((70, 421), Direction.WEST), 4)
        self.planet_wakanda.add_path(((69, 421),Direction.NORTH),((69, 421), Direction.EAST), 1)
        self.planet_wakanda.add_path(((69, 421),Direction.EAST),((69, 421), Direction.NORTH), 1)
        self.planet_wakanda.add_path(((70, 421),Direction.WEST),((69, 421),Direction.SOUTH), 4)
        self.planet_wakanda.add_path(((70, 421),Direction.EAST),((71, 421), Direction.WEST), 1)
        self.planet_wakanda.add_path(((68, 422),Direction.SOUTH),((68, 421), Direction.NORTH), 1) 
        self.planet_wakanda.add_path(((71, 421),Direction.NORTH),((70, 422), Direction.EAST), 5) 
        self.planet_wakanda.add_path(((71, 421),Direction.WEST),((70, 421), Direction.EAST), 1)
        self.planet_wakanda.add_path(((71, 421),Direction.EAST),((70, 420), Direction.EAST), 1)
        self.planet_wakanda.add_path(((70, 422),Direction.EAST),((71, 421), Direction.NORTH), 5)
        self.planet_wakanda.add_path(((70, 420),Direction.EAST),((71, 421), Direction.EAST), 1)
        self.planet_wakanda.add_path(((70, 420),Direction.WEST),((70, 420), Direction.WEST), -1)

    def test_integrity(self):
        """
        This test should check that the dictionary returned by "planet.get_paths()" matches the expected structure
        """
        structure : Dict[Tuple[int, int], Dict[Direction, Tuple[Tuple[int, int], Direction, Weight]]] = { (0,0) : { Direction.NORTH : ((0,0) , Direction.WEST , 1) } }
        # structure muss implementier werden, damit kein UnboundError geworfen wird
        # Der Wert von structure hat keine Bedeutung für diesen Test

        self.assertEqual(type(structure),type(self.planet.get_paths()))
        
    def test_empty_planet(self):
        """
        This test should check that an empty planet really is empty
        """

        self.assertEqual({}, self.planet_empty.get_paths())

    def test_target(self):
        """
        This test should check that the shortest-path algorithm implemented works.

        Requirement: Minimum distance is three nodes (two paths in list returned)
        """
        expacted_path : List[Optional[Tuple[Tuple[int, int], Direction]]] = [((0,0),Direction.NORTH),((0,1),Direction.WEST),((0,2),Direction.WEST)] # bitte anpassen

        start: Tuple[int,int] = (0,0) # bitte anpassen
        target: Tuple[int,int] = (0,3) # bitte anpassen

        self.assertEqual(expacted_path, self.planet.shortest_path(start,target))

    def test_target_not_reachable(self):
        """
        This test should check that a target outside the map or at an unexplored node is not reachable
        """

        start: Tuple[int,int] = (0,0) # bitte anpassen
        target: Tuple[int,int] = (0,4)# bitte anpassen

        self.assertIsNone(self.planet.shortest_path(start,target))


    def test_same_length(self):
        """
        This test should check that the shortest-path algorithm implemented returns a shortest path even if there
        are multiple shortest paths with the same length.

        Requirement: Minimum of two paths with same cost exists, only one is returned by the logic implemented
        """
        expacted_path_1 : List[Optional[Tuple[Tuple[int, int], Direction]]] = [((0,0),Direction.SOUTH),((0,1),Direction.WEST),((0,2),Direction.WEST)] # bitte anpassen
        expacted_path_2 : List[Optional[Tuple[Tuple[int, int], Direction]]] = [((0,0),Direction.NORTH),((0,1),Direction.WEST),((0,2),Direction.WEST)] # bitte anpassen

        start: Tuple[int,int] = (0,0) # bitte anpassen
        target: Tuple[int,int] = (0,3) # bitte anpassen

        # Hinweis: der Erste Weg zu (0,1) ist NORTH, weshalb diesr Weg normalerweise genommen werden soll
        result = self.planet_equal_paths.shortest_path(start, target)
        #print(result)
        
        if result == expacted_path_1 or result == expacted_path_2:
            pass
        else:
            self.fail(str(result))

    def test_target_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target nearby

        Result: Target is reachable
        """
        expacted_path : List[Optional[Tuple[Tuple[int, int], Direction]]] = [((0,0),Direction.NORTH),((0,1),Direction.WEST),((0,2),Direction.WEST)] # bitte anpassen
        
        start: Tuple[int,int] = (0,0) # bitte anpassen
        reachable_target: Tuple[int,int] = (0,3) # bitte anpassen
        
        result = self.planet_with_loop.shortest_path(start, reachable_target) 
        #print(result)
        self.assertEqual(expacted_path,result)
        
    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """

        start: Tuple[int,int] = (0,0) # bitte anpassen
        not_reachable_target: Tuple[int,int] = (0,4) # bitte anpassen

        result = self.planet_with_loop.shortest_path(start, not_reachable_target) 
        # print(result)
        # assertIsNone wirft ein Fehler, wenn result != None
        self.assertIsNone(result)
        
    def test_target_triangle(self):
        """
        This test should check that the shortest-path algorithm implemented works.

        Requirement: Minimum distance is three nodes (two paths in list returned)
        """

        expacted_path : List[Optional[Tuple[Tuple[int, int], Direction]]] = [((0,0),Direction.WEST),((0,2),Direction.WEST)] # bitte anpassen

        start: Tuple[int,int] = (0,0) # bitte anpassen
        target: Tuple[int,int] = (0,3) # bitte anpassen

        result = self.planet_triangle.shortest_path(start,target)
        #print(result)
        self.assertEqual(expacted_path,result)

    def test_target_big_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between the same node while
        searching for a target nearby

        Result: Target is reachable
        """
        expacted_path : List[Optional[Tuple[Tuple[int, int], Direction]]] = [((0,0),Direction.NORTH),((0,1),Direction.WEST),((0,2),Direction.WEST)] # bitte anpassen
        
        start: Tuple[int,int] = (0,0) # bitte anpassen
        reachable_target: Tuple[int,int] = (0,3) # bitte anpassen
        
        result = self.planet_big_loop.shortest_path(start, reachable_target) 
        #print(result)
        self.assertEqual(expacted_path,result)
     
    def test_target_negativ(self):
        """
        Result: Target is not reachable
        """

        start: Tuple[int,int] = (0,0) # bitte anpassen
        not_reachable_target: Tuple[int,int] = (0,3) # bitte anpassen

        result = self.planet_minus_paths.shortest_path(start, not_reachable_target) 
        #print(result)
        # assertIsNone wirft ein Fehler, wenn result != None
        self.assertIsNone(result)
        
    def test_wakanda(self):
        """
        Result: Target is reachable
        """

        expacted = [((70, 420),Direction.EAST),((71, 421),Direction.NORTH)] 

        start: Tuple[int,int] = (70,420) # bitte anpassen
        reachable_target: Tuple[int,int] = (70,422) # bitte anpassen

        result = self.planet_wakanda.shortest_path(start, reachable_target) 
        #print(result)
        # assertIsNone wirft ein Fehler, wenn result != None
        self.assertEqual(result,expacted)
 

if __name__ == "__main__":
    unittest.main()
