import unittest
import logging 
import sys 
import pexpect
import random
import os
import time
import importlib
import importlib.util
import tempfile

from selenium import webdriver

from . import Project

raise NotImplementedError('This test needs refactoring.')

@generate_exercises(38, 39)
class Project9(Project) :

    @classmethod
    def setUpClass(cls):
        cls._words = []
        with open('/usr/share/dict/words') as d :
            for w in d.readlines() :
                cls._words.append(w.strip())

    def setUp(self) :
        filename = self.find_file('project9.py')
        self.assertIsNotNone(filename, "I can't find your project file (project9.py)")
        self.proj = self.import_project(filename)

    def _random_sentence(self, wcount) :
        return ' '.join(random.choices(self._words, k=wcount))

    def _random_blogentry(self) :
        return {
            'text' : self._random_sentence(20),
            'title': self._random_sentence(5),
            }

    def _random_user(self) :
        name = self._random_sentence(1)
        posts = []
        for i in range(random.randint(2,5)) :
            posts.append(self._random_blogentry())
        return name, {
            'email' : self._random_sentence(1),
            'name'  : self._random_sentence(2),
            'posts' : posts
        }

    def _random_blogsite(self) :
        site = {}
        for i in range(random.randint(3, 10)) :
            username, data = self._random_user()
            site[username] = data
        return site
    
    def test_0_check_docstring(self):
        filename = self.find_file('project9.py')
        self.assertIsNotNone(filename, "I can't find your project file (project9.py)")
        self.check_docstring(filename)

    def test_2_list_users_docstring(self) :
        self.assertIsNotNone(self.proj.list_users.__doc__,
                           "Your list_users() function doesn't have a docstring.")

    def test_2_list_users_function(self) :
        blog = self._random_blogsite()
        got = sorted(self.proj.list_users(blog))
        expect = sorted(list(blog.keys()))
        self.assertEqual(got, expect, "list_users() didn't return the expected set of users")

    def test_3_user_summary_docstring(self) :
        self.assertIsNotNone(self.proj.user_summary.__doc__,
                           "Your user_summary() function doesn't have a docstring.")

    def test_3_user_summary_function(self) :
        blog = self._random_blogsite()
        user = random.choice(list(blog.keys()))
        got = sorted(self.proj.user_summary(blog, user))
        expect = sorted([x['title'] for x in blog[user]['posts']])
        self.assertEqual(got, expect, "user_summary() didn't return the expected titles")
    
    def test_4_update_user_info_docstring(self) :
        self.assertIsNotNone(self.proj.update_user_info.__doc__,
                           "Your update_user_info() function doesn't have a docstring.")

    def test_4_update_user_info_function(self) :
        blog = self._random_blogsite()
        user = random.choice(list(blog.keys()))

        old_email = blog[user]['email']
        old_name = blog[user]['name']
        new_email = self._random_sentence(1)
        new_name = self._random_sentence(1)

        self.proj.update_user_info(blog, user, None, None)
        self.assertEqual(blog[user]['name'], old_name, 'You updated name when I passed None')
        self.assertEqual(blog[user]['email'], old_email, 'You updated email when I passed None')
        
        self.proj.update_user_info(blog, user, new_name, None)
        self.assertEqual(blog[user]['name'], new_name, 'You failed to update name')
        self.assertEqual(blog[user]['email'], old_email, 'You updated email when I passed None')

        self.proj.update_user_info(blog, user, None, new_email)
        self.assertEqual(blog[user]['name'], new_name, 'You updated name when I passed None')
        self.assertEqual(blog[user]['email'], new_email, 'You failed to update email')
        
        self.proj.update_user_info(blog, user, old_name, old_email)
        self.assertEqual(blog[user]['name'], old_name, 'You failed to update name')
        self.assertEqual(blog[user]['email'], old_email, 'You failed to update email')
        
    def test_5_delete_post_docstring(self) :
        self.assertIsNotNone(self.proj.delete_post.__doc__,
                           "Your delete_post() function doesn't have a docstring.")

    def test_5_delete_post_function(self) :
        blog = self._random_blogsite()
        user = random.choice(list(blog.keys()))
        post = random.randint(1, len(blog[user]['posts'])-1)

        deleted = self.proj.delete_post(blog, user, post)
        if deleted in blog[user]['posts'] :
            self.fail('The deleted post still appears in the data structure.')
        
        
if __name__ == '__main__' : 
    unittest.main(verbosity=2, exit=False)
