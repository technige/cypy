#!/usr/bin/env python
# coding: utf-8

# Copyright 2002-2018, Neo4j
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from unittest import TestCase

import cypy
from cypy.graph.store import FrozenGraphStore, MutableGraphStore

_n = 65


def _counter():
    global _n
    try:
        return chr(_n)
    finally:
        _n += 1

cypy.graph.store.new_key = _counter


class GraphStoreTestCase(TestCase):

    store = MutableGraphStore()
    a, b, c, d = store.add_nodes((
        (["X"], {"name": "Alice"}),
        (["X", "Y"], {"name": "Bob"}),
        (["X", "Y"], {"name": "Carol"}),
        (["Y"], {"name": "Dave"}),
    ))
    a_likes_b, b_likes_a, a_knows_b, a_knows_c, \
    c_knows_b, c_married_to_d = store.add_relationships((
        ("LIKES", (a, b), {}),
        ("LIKES", (b, a), {}),
        ("KNOWS", (a, b), {"since": 1999}),
        ("KNOWS", (a, c), {"since": 2000}),
        ("KNOWS", (c, b), {"since": 2001}),
        ("MARRIED_TO", (c, d), {}),
    ))

    def test_should_reflect_self_in_store_magic_method(self):
        store = FrozenGraphStore(self.store)
        assert store.__graph_store__() is store

    def test_should_get_counts(self):
        store = FrozenGraphStore(self.store)
        assert store.node_count() == 4
        assert store.node_count("X") == 3
        assert store.relationship_count() == 6
        assert store.relationship_count("KNOWS") == 3
        assert store.node_labels() == {"X", "Y"}
        assert store.relationship_types() == {"LIKES", "KNOWS", "MARRIED_TO"}

    def test_should_get_node_degree(self):
        store = FrozenGraphStore(self.store)
        assert store.relationship_count(n_ids={self.a}) == 4
        assert store.relationship_count(r_type="LIKES", n_ids={self.a}) == 2
        assert store.relationship_count(n_ids={self.b}) == 4
        assert store.relationship_count(n_ids={self.c}) == 3
        assert store.relationship_count(n_ids={self.d}) == 1

    def test_should_get_nodes(self):
        store = FrozenGraphStore(self.store)
        assert set(store.nodes()) == {self.a, self.b, self.c, self.d}

    def test_should_get_nodes_with_a_label(self):
        store = FrozenGraphStore(self.store)
        assert set(store.nodes("X")) == {self.a, self.b, self.c}
        assert set(store.nodes("Y")) == {self.b, self.c, self.d}
        assert not set(store.nodes("Z"))

    def test_should_get_nodes_with_multiple_labels(self):
        store = FrozenGraphStore(self.store)
        assert set(store.nodes("X", "Y")) == {self.b, self.c}
        assert not set(store.nodes("X", "Z"))

    def test_should_get_node_labels(self):
        store = FrozenGraphStore(self.store)
        assert store.node_labels() == {"X", "Y"}
        assert store.node_labels(self.a) == {"X"}
        assert store.node_labels(self.b) == {"X", "Y"}
        assert store.node_labels(self.c) == {"X", "Y"}
        assert store.node_labels(self.d) == {"Y"}
        assert store.node_labels(object()) is None

    def test_should_get_node_properties(self):
        store = FrozenGraphStore(self.store)
        assert store.node_properties(self.a) == {"name": "Alice"}
        assert store.node_properties(self.b) == {"name": "Bob"}
        assert store.node_properties(self.c) == {"name": "Carol"}
        assert store.node_properties(self.d) == {"name": "Dave"}
        assert store.node_properties(object()) is None

    def test_should_get_relationships(self):
        store = FrozenGraphStore(self.store)
        assert set(store.relationships()) == {self.a_likes_b, self.b_likes_a, self.a_knows_b, self.a_knows_c, self.c_knows_b, self.c_married_to_d}
        assert set(store.relationships("KNOWS")) == {self.a_knows_b, self.a_knows_c, self.c_knows_b}
        assert set(store.relationships("MARRIED_TO")) == {self.c_married_to_d}
        assert set(store.relationships(n_ids=(self.a, None))) == {self.a_likes_b, self.a_knows_b, self.a_knows_c}
        assert set(store.relationships("KNOWS", (self.a, None))) == {self.a_knows_b, self.a_knows_c}
        assert set(store.relationships(n_ids=(None, self.b))) == {self.a_likes_b, self.a_knows_b, self.c_knows_b}
        assert set(store.relationships("KNOWS", n_ids=(None, self.b))) == {self.a_knows_b, self.c_knows_b}
        assert set(store.relationships(n_ids=(self.a, self.b))) == {self.a_likes_b, self.a_knows_b}
        assert set(store.relationships("KNOWS", (self.a, self.b))) == {self.a_knows_b}
        assert set(store.relationships(n_ids={self.a})) == {self.a_likes_b, self.b_likes_a, self.a_knows_b, self.a_knows_c}
        assert set(store.relationships("KNOWS", {self.a})) == {self.a_knows_b, self.a_knows_c}
        assert set(store.relationships(n_ids={self.a, self.b})) == {self.a_likes_b, self.b_likes_a, self.a_knows_b}
        assert set(store.relationships("KNOWS", n_ids={self.a, self.b})) == {self.a_knows_b}

    def test_should_fail_on_bad_node_sequence(self):
        store = FrozenGraphStore(self.store)
        assert list(store.relationships(n_ids=(self.a, self.b, self.c))) == []

    def test_should_fail_on_bad_node_set(self):
        store = FrozenGraphStore(self.store)
        _ = store.relationships(n_ids={self.a, self.b, self.c})

    def test_should_fail_on_bad_node_type(self):
        store = FrozenGraphStore(self.store)
        with self.assertRaises(TypeError):
            _ = store.relationships(n_ids=1)

    def test_should_get_relationship_nodes(self):
        store = FrozenGraphStore(self.store)
        assert store.relationship_nodes(self.a_likes_b) == (self.a, self.b)
        assert store.relationship_nodes(self.b_likes_a) == (self.b, self.a)
        assert store.relationship_nodes(self.a_knows_b) == (self.a, self.b)
        assert store.relationship_nodes(self.a_knows_c) == (self.a, self.c)
        assert store.relationship_nodes(self.c_knows_b) == (self.c, self.b)
        assert store.relationship_nodes(self.c_married_to_d) == (self.c, self.d)
        assert store.relationship_nodes(object()) is None

    def test_should_get_relationship_properties(self):
        store = FrozenGraphStore(self.store)
        assert store.relationship_properties(self.a_knows_b) == {"since": 1999}
        assert store.relationship_properties(self.a_knows_c) == {"since": 2000}
        assert store.relationship_properties(self.c_knows_b) == {"since": 2001}
        assert store.relationship_properties(object()) is None

    def test_should_get_relationship_type(self):
        store = FrozenGraphStore(self.store)
        assert store.relationship_type(self.a_likes_b) == "LIKES"
        assert store.relationship_type(self.b_likes_a) == "LIKES"
        assert store.relationship_type(self.a_knows_b) == "KNOWS"
        assert store.relationship_type(self.a_knows_c) == "KNOWS"
        assert store.relationship_type(self.c_knows_b) == "KNOWS"
        assert store.relationship_type(self.c_married_to_d) == "MARRIED_TO"
        assert store.relationship_type(object()) is None


class FrozenGraphStoreTestCase(TestCase):

    store = MutableGraphStore()
    a, b, c, d = store.add_nodes((
        (["X"], {"name": "Alice"}),
        (["X", "Y"], {"name": "Bob"}),
        (["X", "Y"], {"name": "Carol"}),
        (["Y"], {"name": "Dave"}),
    ))
    store.add_relationships((
        ("KNOWS", (a, b), {}),
        ("KNOWS", (a, c), {}),
        ("KNOWS", (b, c), {}),
        ("KNOWS", (c, d), {}),
    ))
    store = FrozenGraphStore(store)

    def test_should_create_empty_on_none(self):
        store = FrozenGraphStore()
        assert store.node_count() == 0
        assert store.relationship_count() == 0
        assert not store.node_labels()
        assert not store.relationship_types()

    def test_should_not_create_from_non_store(self):
        with self.assertRaises(TypeError):
            _ = FrozenGraphStore(object())

    def test_should_create_copy_of_frozen_store(self):
        store = FrozenGraphStore(FrozenGraphStore(self.store))
        assert store.node_count() == 4
        assert store.relationship_count() == 4
        assert store.node_labels() == {"X", "Y"}
        assert store.relationship_types() == {"KNOWS"}

    def test_should_create_copy_of_mutable_store(self):
        store = FrozenGraphStore(self.store)
        assert store.node_count() == 4
        assert store.relationship_count() == 4
        assert store.node_labels() == {"X", "Y"}
        assert store.relationship_types() == {"KNOWS"}

    def test_should_allow_construction_arguments(self):
        store = FrozenGraphStore.build({
            "a": (["Person"], {"name": "Alice", "age": 33}),
            "b": (["Person"], {"name": "Bob", "age": 44}),
        }, {
            "ab": ("KNOWS", ("a", "b"), {"since": 1999}),
        })
        assert isinstance(store, FrozenGraphStore)
        assert store.node_count() == 2
        assert store.relationship_count() == 1
        assert store.node_labels() == {"Person"}
        assert store.relationship_types() == {"KNOWS"}
        assert set(store.nodes("Person")) == {"a", "b"}
        assert store.node_labels("a") == {"Person"}
        assert store.node_labels("b") == {"Person"}
        assert store.node_properties("a") == {"name": "Alice", "age": 33}
        assert store.node_properties("b") == {"name": "Bob", "age": 44}
        assert set(store.relationships("KNOWS")) == {"ab"}
        assert store.relationship_type("ab") == "KNOWS"
        assert store.relationship_properties("ab") == {"since": 1999}


class MutableGraphStoreTestCase(TestCase):

    store = MutableGraphStore()
    a, b, c, d = store.add_nodes((
        (["X"], {"name": "Alice"}),
        (["X", "Y"], {"name": "Bob"}),
        (["X", "Y"], {"name": "Carol"}),
        (["Y"], {"name": "Dave"}),
    ))
    store.add_relationships((
        ("KNOWS", (a, b), {}),
        ("KNOWS", (a, c), {}),
        ("KNOWS", (b, c), {}),
        ("KNOWS", (c, d), {}),
    ))

    def test_should_create_empty_on_none(self):
        store = MutableGraphStore()
        assert store.node_count() == 0
        assert store.relationship_count() == 0
        assert not store.node_labels()
        assert not store.relationship_types()

    def test_should_create_copy_of_frozen_store(self):
        store = MutableGraphStore(FrozenGraphStore(self.store))
        assert store.node_count() == 4
        assert store.relationship_count() == 4
        assert store.node_labels() == {"X", "Y"}
        assert store.relationship_types() == {"KNOWS"}

    def test_should_create_copy_of_mutable_store(self):
        store = MutableGraphStore(self.store)
        assert store.node_count() == 4
        assert store.relationship_count() == 4
        assert store.node_labels() == {"X", "Y"}
        assert store.relationship_types() == {"KNOWS"}

    def test_can_add_new_label(self):
        store = MutableGraphStore(self.store)
        labels = store.node_labels(self.a)
        assert labels == {"X"}
        labels.add("Z")
        assert store.node_labels(self.a) == {"X", "Z"}
        assert "Z" in set(store.node_labels())

    def test_can_add_existing_label(self):
        store = MutableGraphStore(self.store)
        labels = store.node_labels(self.a)
        assert labels == {"X"}
        labels.add("X")
        assert store.node_labels(self.a) == {"X"}

    def test_can_remove_label(self):
        store = MutableGraphStore(self.store)
        labels = store.node_labels(self.a)
        assert labels == {"X"}
        labels.remove("X")
        assert not store.node_labels(self.a)

    def test_can_discard_label(self):
        store = MutableGraphStore(self.store)
        labels = store.node_labels(self.a)
        assert labels == {"X"}
        labels.discard("Z")
        assert store.node_labels(self.a) == {"X"}

    def test_can_clear_labels(self):
        store = MutableGraphStore(self.store)
        labels = store.node_labels(self.b)
        assert labels == {"X", "Y"}
        labels.clear()
        assert not store.node_labels(self.b)

    def test_can_add_properties(self):
        store = MutableGraphStore(self.store)
        properties = store.node_properties(self.a)
        assert properties == {"name": "Alice"}
        properties["age"] = 33
        assert store.node_properties(self.a) == {"name": "Alice", "age": 33}

    def test_can_update_properties(self):
        store = MutableGraphStore(self.store)
        properties = store.node_properties(self.a)
        assert properties == {"name": "Alice"}
        properties["name"] = "Alistair"
        assert store.node_properties(self.a) == {"name": "Alistair"}

    def test_can_remove_properties(self):
        store = MutableGraphStore(self.store)
        properties = store.node_properties(self.a)
        assert properties == {"name": "Alice"}
        del properties["name"]
        assert store.node_properties(self.a) == {}

    def test_should_allow_construction_arguments(self):
        store = MutableGraphStore.build({
            "a": (["Person"], {"name": "Alice", "age": 33}),
            "b": (["Person"], {"name": "Bob", "age": 44}),
        }, {
            "ab": ("KNOWS", ("a", "b"), {"since": 1999}),
        })
        assert isinstance(store, MutableGraphStore)
        assert store.node_count() == 2
        assert store.relationship_count() == 1
        assert store.node_labels() == {"Person"}
        assert store.relationship_types() == {"KNOWS"}
        assert set(store.nodes("Person")) == {"a", "b"}
        assert store.node_labels("a") == {"Person"}
        assert store.node_labels("b") == {"Person"}
        assert store.node_properties("a") == {"name": "Alice", "age": 33}
        assert store.node_properties("b") == {"name": "Bob", "age": 44}
        assert set(store.relationships(r_type="KNOWS")) == {"ab"}
        assert store.relationship_type("ab") == "KNOWS"
        assert store.relationship_properties("ab") == {"since": 1999}