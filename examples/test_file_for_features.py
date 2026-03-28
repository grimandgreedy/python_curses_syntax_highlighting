#!/usr/bin/env python3
"""Test file to demonstrate wrap and indent features.

This file has:
- Very long lines to test word wrap functionality properly and see how it handles wrapping in different scenarios
- Multiple levels of indentation to test indent guide visibility
"""

def example_function_with_long_lines():
    """This is a very long docstring that should definitely wrap when the terminal is not wide enough to display it all on a single line."""
    if True:
        if True:
            if True:
                if True:
                    # This is deeply indented to show indent guides at every 4-space boundary
                    result = "This is a very long string literal that will definitely wrap around when displayed in a narrow terminal window or when word wrap is enabled in the viewer"
                    another_long_variable_name = "Another extremely long line of code that should wrap around and demonstrate the word wrap feature working correctly when toggled on and off"

                    # More indentation
                    nested_dict = {
                        "key1": "This is a very long value string that should wrap",
                        "key2": "Another long value to demonstrate wrapping behavior",
                        "key3": {
                            "nested_key1": "Deeply nested value with a very long string",
                            "nested_key2": "Another deeply nested long string value here",
                        }
                    }

                    return result + another_long_variable_name


class ExampleClass:
    """Class to demonstrate indentation."""

    def method_one(self):
        """Method with indentation."""
        if True:
            if True:
                if True:
                    if True:
                        # Deep indentation shows indent guides clearly
                        print("Four levels of indentation - you should see indent guides at each level")

    def method_two_with_very_long_name_that_will_cause_wrapping_when_parameters_are_added(self, parameter_one, parameter_two, parameter_three):
        """This method signature is very long and should wrap nicely."""
        return parameter_one + parameter_two + parameter_three


# Some code with various indentation levels
for i in range(10):
    for j in range(10):
        for k in range(10):
            for l in range(10):
                # Four levels deep - indent guides should be very visible
                value = i * j * k * l
                if value > 100:
                    print(f"Value is {value} which is a result of multiplying {i} * {j} * {k} * {l}")
