name: Bug Report
description: File a bug report
title: '[BUG] <title>'
labels:
  - bug
  - priority:low
  - status:review_needed
body:
  - type: markdown
    attributes:
      value: |
        **Thank you for wanting to report a bug!**

        ⚠ Please make sure that this [issue wasn't already requested][issue search], or already implemented in the master branch.

  - type: textarea
    attributes:
      label: Bug Description
      description: >-
        What is the bug? Please provide a snippet of the output including
        any errors and the messages logged before the error.
        Verbose or debug logs are preferred but please ensure all secrets and
        other sensitive information has been removed.
      placeholder: I did ... and ... happened.
    validations:
      required: true
  - type: textarea
    attributes:
      label: Expected Behavior
      description: |
        What did you expect to happen? For example, expected output or behavior.
    validations:
      required: true
  - type: textarea
    attributes:
      label: Steps To Reproduce
      description: >-
        Please provide the steps that can be used to reproduce this behavior.

      value: |
        Example: ...

        1.
        2.
        3.
        ...
    validations:
      required: true
  - type: input
    attributes:
      label: Version
      description: This can be found by [enter description].
      placeholder: 0.0.0
    validations:
      required: false
  - type: textarea
    attributes:
      label: OS / Environment
      description: |
        Provide all relevant information below, e.g. OS version, language versions.

        examples:
          - **OS:** macOS 11
          - **python version:** 3.10.0
          - **npm version:** 7.20.0
          - **terraform version:** 1.0.0
          - **serverless version:** 2.0.0

      placeholder: |
        - OS: macOS 11
        - python version: 3.10.0
        - npm version: 7.20.0
        - terraform version: 1.0.0
        - serverless version: 2.0.0
    validations:
      required: false
  - type: textarea
    attributes:
      label: Anything else?
      description: |
        Links? References? Anything that will give us more context about the issue you are encountering!

        Tip: You can attach images or log files by clicking this area to highlight it and then dragging files in.
    validations:
      required: false