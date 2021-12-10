import typing

from .CppFieldGenerator import CppFieldGenerator
from .CppTypesGenerator import CppTypesGenerator


class CppPrintOutputGenerator():
    """
    Generates a 'Print()' C++ method to pretty print deserialized raw byte buffer inputs.
    Fields are added for printing by calling 'xyz_field()' methods and when done the C++ 
    print method is generated by calling the 'generate()' method.
    """

    def __init__( self, types: CppTypesGenerator, class_name: str, size_to_arrays : typing.Dict[str, typing.List[str]] ) -> None:
        self.__name_to_enum   = types.name_to_enum
        self.__name_to_type   = types.name_to_type
        self.__size_to_arrays = size_to_arrays

        self.__code_output   = f'void {class_name}::Print( size_t level )\n{{\n'
        self.__code_output  += f"\tstd::string tabs( level, '\\t' );\n"
        self.__code_output  += f'\tstd::cout << tabs << "{class_name}\\n";\n'
        self.__code_output  += f'\tstd::cout << tabs << "{{\\n";\n\n'



    def normal_field( self, var_type: str, var_name: str ):
        member_name = CppFieldGenerator.convert_to_field_name(var_name)

        if var_type in self.__name_to_type:
            typedef = self.__name_to_type[var_type]

            if typedef.size == 1:
                self.__code_output += f'\tstd::cout << tabs << "\\t{var_type} {member_name}: " << +(static_cast<{typedef.type}>({member_name})) << "\\n";\n'
            else:
                self.__code_output += f'\n'
                self.__code_output += f'\tstd::cout << tabs << "\\t{typedef.type} " << "{member_name}[ " << {typedef.size} << " ] = |";\n'
                self.__code_output += f'\tfor( size_t j=0; j<{typedef.size}; ++j )\n'
                self.__code_output += f'\t{{\n'
                self.__code_output += f'\t\tstd::cout << std::setfill(\'0\') << /*std::setw(2) << std::hex <<*/ +{member_name}.data[j] << "|";\n'
                self.__code_output += f'\t}}\n'
                self.__code_output += f'\tstd::cout << "\\n";\n'

        elif var_type in self.__name_to_enum:
            enum_type = self.__name_to_enum[var_type].type
            self.__code_output += f'\tstd::cout << tabs << "\\t{var_type} {member_name}: " << +static_cast<{enum_type}>({member_name}) << "\\n";\n'

        elif var_type in CppFieldGenerator.builtin_types:

            if var_name in self.__size_to_arrays:
                array_name = self.__size_to_arrays[var_name][0]
                array_name = CppFieldGenerator.convert_to_field_name(array_name)
                self.__code_output += f'\tstd::cout << tabs << "\\t{var_type} {member_name}: " << {array_name}.size() << "\\n";\n'
            else:
                self.__code_output += f'\tstd::cout << tabs << "\\t{var_type} {member_name}: " << +{member_name} << "\\n";\n'

        else:
            self.__code_output += f'\t{member_name}.Print( level+1 );\n'



    def array_field( self, array_type: str, array_name: str ):
        arr_member_name = CppFieldGenerator.convert_to_field_name( array_name )

        self.__code_output += f'\n'
        self.__code_output += f'\tstd::cout << tabs << "\\t{array_type} " << "{arr_member_name}[ " << {arr_member_name}.size() << " ] =\\n";\n' 
        self.__code_output += f'\tstd::cout << tabs << "\\t[\\n";\n'
        self.__code_output += f'\tfor( size_t i=0; i<{arr_member_name}.size(); ++i )\n'
        self.__code_output += f'\t{{\n'

        self.normal_field(array_type, array_name+'[i]')

        self.__code_output += f'\t}}\n'
        self.__code_output += f'\tstd::cout << tabs <<"\\t]\\n";\n'



    def inline_field( self, var_name: str ):
        var_name = CppFieldGenerator.convert_to_field_name(var_name)
        self.__code_output += f'\t{var_name}.Print( level+1 );\n'



    def reserved_field( self, var_type: str, var_name: str, var_value: str ):
        self.__code_output += f'\tstd::cout << tabs << "\\t{var_type} {var_name}: " << {var_value} << "\\n";\n'



    def array_sized_field( self, array_type: str, array_name: str, array_size: str ):
        array_name = CppFieldGenerator.convert_to_field_name(array_name)
        array_size = CppFieldGenerator.convert_to_field_name(array_size)

        self.__code_output += f'\tstd::cout << tabs << "\\t{array_type} " << "{array_name}[ " << {array_name}.size() << " ] =\\n";\n' 
        self.__code_output += f'\tstd::cout << tabs << "\\t[\\n";\n'
        self.__code_output += f'\tfor( size_t i=0; i<{array_name}.size(); ++i )\n'
        self.__code_output += f'\t{{\n'
        self.__code_output += f'\t\t{array_name}[i]->Print( level+1 );'
        self.__code_output += f'\t}}\n'



    def array_fill_field( self, array_type: str, array_name: str ):
        self.array_field( array_type, array_name )



    def condition( self, var_type: str, var_name: str, condition: str, union_name: str = "" ):
        self.__code_output += f'\tstd::cout << tabs << "\\tTODO: to be implemented when unions implemented in schemas!!!: if( {condition} ) {var_type} {var_name}\\n";\n'
        #TODO: implement this when unions and 



    def generate( self ) -> str:
        self.__code_output  += '\n\tstd::cout << tabs << "}\\n";\n'
        self.__code_output  += "}\n"
        return self.__code_output
