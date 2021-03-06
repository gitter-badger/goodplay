# -*- coding: utf-8 -*-

import pytest

from goodplay_helpers import smart_create

pytestmark = pytest.mark.integration


def test_passed_on_selfcontained_role(testdir):
    smart_create(testdir.tmpdir, '''
    ## local-role-base/role1/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies: []

    ## local-role-base/role1/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role1.run"
        state: touch

    ## local-role-base/role1/tests/inventory
    127.0.0.1 ansible_connection=local

    ## local-role-base/role1/tests/test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      roles:
        - role: role1

    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: assert role1 run
          file:
            path: "{{ playbook_dir }}/.role1.run"
            state: file
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)


def test_failed_on_selfcontained_role_without_meta(testdir):
    smart_create(testdir.tmpdir, '''
    ## local-role-base/role1/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role1.run"
        state: touch

    ## local-role-base/role1/tests/inventory
    127.0.0.1 ansible_connection=local

    ## local-role-base/role1/tests/test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      roles:
        - role: role1

    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: assert role1 run
          file:
            path: "{{ playbook_dir }}/.role1.run"
            state: file
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(failed=1)


def test_passed_on_role_with_dependent_role_beside(testdir):
    smart_create(testdir.tmpdir, '''
    ## external-role-base/role1.tar.gz
    #### role1/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies: []

    #### role1/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role1external.run"
        state: touch

    ## local-role-base/role1/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies: []

    ## local-role-base/role1/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role1local.run"
        state: touch

    ## local-role-base/role2/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies:
      - name: role1
        src: external-role-base/role1.tar.gz

    ## local-role-base/role2/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role2.run"
        state: touch

    ## local-role-base/role2/tests/inventory
    127.0.0.1 ansible_connection=local

    ## local-role-base/role2/tests/test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      roles:
        - role: role2

    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: assert role1external not run
          file:
            path: "{{ playbook_dir }}/.role1external.run"
            state: absent
          tags: test

        - name: assert role1local run
          file:
            path: "{{ playbook_dir }}/.role1local.run"
            state: file
          tags: test

        - name: assert role2 run
          file:
            path: "{{ playbook_dir }}/.role2.run"
            state: file
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=3)


def test_passed_on_role_with_multi_level_dependent_role_beside(testdir):
    smart_create(testdir.tmpdir, '''
    ## external-role-base/role1.tar.gz
    #### role1/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies: []

    #### role1/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role1external.run"
        state: touch

    ## local-role-base/role1/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies: []

    ## local-role-base/role1/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role1local.run"
        state: touch

    ## external-role-base/role2.tar.gz
    #### role2/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies:
      - name: role1
        src: external-role-base/role1.tar.gz

    #### role2/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role2external.run"
        state: touch

    ## local-role-base/role2/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies:
      - name: role1
        src: external-role-base/role1.tar.gz

    ## local-role-base/role2/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role2local.run"
        state: touch

    ## local-role-base/role3/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies:
      - name: role2
        src: external-role-base/role2.tar.gz

    ## local-role-base/role3/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role3.run"
        state: touch

    ## local-role-base/role3/tests/inventory
    127.0.0.1 ansible_connection=local

    ## local-role-base/role3/tests/test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      roles:
        - role: role3

    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: assert role1external not run
          file:
            path: "{{ playbook_dir }}/.role1external.run"
            state: absent
          tags: test

        - name: assert role1local run
          file:
            path: "{{ playbook_dir }}/.role1local.run"
            state: file
          tags: test

        - name: assert role2external not run
          file:
            path: "{{ playbook_dir }}/.role2external.run"
            state: absent
          tags: test

        - name: assert role2local run
          file:
            path: "{{ playbook_dir }}/.role2local.run"
            state: file
          tags: test

        - name: assert role3 run
          file:
            path: "{{ playbook_dir }}/.role3.run"
            state: file
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=5)


def test_passed_on_role_with_external_dependent_role(testdir):
    smart_create(testdir.tmpdir, '''
    ## external-role-base/role1.tar.gz
    #### role1/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies: []

    #### role1/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role1.run"
        state: touch

    ## local-role-base/role2/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies:
      - name: role1
        src: external-role-base/role1.tar.gz

    ## local-role-base/role2/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role2.run"
        state: touch

    ## local-role-base/role2/tests/inventory
    127.0.0.1 ansible_connection=local

    ## local-role-base/role2/tests/test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      roles:
        - role: role2

    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: assert role1 run
          file:
            path: "{{ playbook_dir }}/.role1.run"
            state: file
          tags: test

        - name: assert role2 run
          file:
            path: "{{ playbook_dir }}/.role2.run"
            state: file
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=2)


def test_passed_on_role_with_multi_level_external_dependent_role(testdir):
    smart_create(testdir.tmpdir, '''
    ## external-role-base/role1.tar.gz
    #### role1/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies: []

    #### role1/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role1.run"
        state: touch

    ## external-role-base/role2.tar.gz
    #### role2/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies:
      - name: role1
        src: external-role-base/role1.tar.gz

    #### role2/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role2.run"
        state: touch

    ## local-role-base/role3/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies:
      - name: role2
        src: external-role-base/role2.tar.gz

    ## local-role-base/role3/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role3.run"
        state: touch

    ## local-role-base/role3/tests/inventory
    127.0.0.1 ansible_connection=local

    ## local-role-base/role3/tests/test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      roles:
        - role: role3

    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: assert role1 run
          file:
            path: "{{ playbook_dir }}/.role1.run"
            state: file
          tags: test

        - name: assert role2 run
          file:
            path: "{{ playbook_dir }}/.role2.run"
            state: file
          tags: test

        - name: assert role3 run
          file:
            path: "{{ playbook_dir }}/.role3.run"
            state: file
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=3)


def test_passed_on_role_with_external_soft_dependent_role(testdir):
    smart_create(testdir.tmpdir, '''
    ## external-role-base/role1.tar.gz
    #### role1/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies: []

    #### role1/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role1.run"
        state: touch

    ## local-role-base/role2/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies: []

    ## local-role-base/role2/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role2.run"
        state: touch

    ## local-role-base/role2/tests/inventory
    127.0.0.1 ansible_connection=local

    ## local-role-base/role2/tests/requirements.yml
    - name: role1
      src: external-role-base/role1.tar.gz

    ## local-role-base/role2/tests/test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      roles:
        - role: role1
        - role: role2

    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: assert role1 run
          file:
            path: "{{ playbook_dir }}/.role1.run"
            state: file
          tags: test

        - name: assert role2 run
          file:
            path: "{{ playbook_dir }}/.role2.run"
            state: file
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=2)


def test_passed_on_role_with_multi_level_external_soft_dependent_role(testdir):
    smart_create(testdir.tmpdir, '''
    ## external-role-base/role1.tar.gz
    #### role1/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies: []

    #### role1/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role1.run"
        state: touch

    ## external-role-base/role2.tar.gz
    #### role2/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies:
      - name: role1
        src: external-role-base/role1.tar.gz

    #### role2/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role2.run"
        state: touch

    ## local-role-base/role3/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies: []

    ## local-role-base/role3/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role3.run"
        state: touch

    ## local-role-base/role3/tests/inventory
    127.0.0.1 ansible_connection=local

    ## local-role-base/role3/tests/requirements.yml
    - name: role2
      src: external-role-base/role2.tar.gz

    ## local-role-base/role3/tests/test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      roles:
        - role: role2
        - role: role3

    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: assert role1 run
          file:
            path: "{{ playbook_dir }}/.role1.run"
            state: file
          tags: test

        - name: assert role2 run
          file:
            path: "{{ playbook_dir }}/.role2.run"
            state: file
          tags: test

        - name: assert role3 run
          file:
            path: "{{ playbook_dir }}/.role3.run"
            state: file
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=3)


def test_dependency_beside_takes_precedence_over_soft_dependency(testdir):
    smart_create(testdir.tmpdir, '''
    ## external-role-base/role1soft.tar.gz
    #### role1soft/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies: []

    #### role1soft/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role1soft.run"
        state: touch

    ## local-role-base/role1/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies: []

    ## local-role-base/role1/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role1.run"
        state: touch

    ## local-role-base/role2/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies: []

    ## local-role-base/role2/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role2.run"
        state: touch

    ## local-role-base/role2/tests/inventory
    127.0.0.1 ansible_connection=local

    ## local-role-base/role2/tests/requirements.yml
    - name: role1
      src: external-role-base/role1soft.tar.gz

    ## local-role-base/role2/tests/test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      roles:
        - role: role1
        - role: role2

    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: assert role1 run
          file:
            path: "{{ playbook_dir }}/.role1.run"
            state: file
          tags: test

        - name: assert role1soft not run
          file:
            path: "{{ playbook_dir }}/.role1soft.run"
            state: absent
          tags: test

        - name: assert role2 run
          file:
            path: "{{ playbook_dir }}/.role2.run"
            state: file
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=3)


def test_dependency_beside_takes_precedence_over_role_dependency(testdir):
    smart_create(testdir.tmpdir, '''
    ## external-role-base/role1.tar.gz
    #### role1/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies: []

    #### role1/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role1external.run"
        state: touch

    ## local-role-base/role1/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies: []

    ## local-role-base/role1/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role1local.run"
        state: touch

    ## local-role-base/role2/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies:
      - name: role1
        src: external-role-base/role1.tar.gz

    ## local-role-base/role2/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role2.run"
        state: touch

    ## local-role-base/role2/tests/inventory
    127.0.0.1 ansible_connection=local

    ## local-role-base/role2/tests/test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      roles:
        - role: role2

    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: assert role1local run
          file:
            path: "{{ playbook_dir }}/.role1local.run"
            state: file
          tags: test

        - name: assert role1external not run
          file:
            path: "{{ playbook_dir }}/.role1external.run"
            state: absent
          tags: test

        - name: assert role2 run
          file:
            path: "{{ playbook_dir }}/.role2.run"
            state: file
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=3)


def test_soft_dependency_takes_precedence_over_role_dependency(testdir):
    smart_create(testdir.tmpdir, '''
    ## external-role-base/role1.tar.gz
    #### role1/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies: []

    #### role1/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role1.run"
        state: touch

    ## external-role-base/role1soft.tar.gz
    #### role1soft/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies: []

    #### role1soft/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role1soft.run"
        state: touch

    ## local-role-base/role2/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies:
      - name: role1
        src: external-role-base/role1.tar.gz

    ## local-role-base/role2/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role2.run"
        state: touch

    ## local-role-base/role2/tests/inventory
    127.0.0.1 ansible_connection=local

    ## local-role-base/role2/tests/requirements.yml
    - name: role1
      src: external-role-base/role1soft.tar.gz

    ## local-role-base/role2/tests/test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      roles:
        - role: role2

    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: assert role1 not run
          file:
            path: "{{ playbook_dir }}/.role1.run"
            state: absent
          tags: test

        - name: assert role1soft run
          file:
            path: "{{ playbook_dir }}/.role1soft.run"
            state: file
          tags: test

        - name: assert role2 run
          file:
            path: "{{ playbook_dir }}/.role2.run"
            state: file
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=3)


def test_failed_on_unresolvable_role(testdir):
    smart_create(testdir.tmpdir, '''
    ## local-role-base/role1/meta/main.yml
    galaxy_info:
      author: John Doe
    dependencies: []

    ## local-role-base/role1/tasks/main.yml
    - file:
        path: "{{ playbook_dir }}/.role1.run"
        state: touch

    ## local-role-base/role1/tests/inventory
    127.0.0.1 ansible_connection=local

    ## local-role-base/role1/tests/test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      roles:
        - role: role2

    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: task1
          ping:
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(failed=1)
