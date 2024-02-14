import os
import re

with open("packets/custom.c", "r") as f:
    custom_code = f.read()

type_map = {
    #  TYPE  |code tpye             |method type       |is heap
    "b": ["char ", "char", False],
    "B": ["unsigned char ", "byte", False],
    "h": ["short ", "short", False],
    "H": ["unsigned short ", "ushort", False],
    "i": ["int ", "int", False],
    "I": ["unsigned int ", "uint", False],
    "l": ["long ", "long", False],
    "L": ["unsigned long ", "ulong", False],
    "f": ["float ", "float", False],
    "d": ["double ", "double", False],
    "q": ["long long ", "llong", False],
    "Q": ["unsigned long long ", "ullong", False],
    "?": ["bool ", "bool", False],
    "v": ["int ", "varint", False],
    "s": ["char *", "string", True],
    "p": ["cmc_block_pos ", "position", False],
    "n": ["cmc_nbt_node *", "nbt", True],
    "a": ["cmc_buffer *", "byte_array", True],
    "S": ["cmc_slot *", "slot", True],
    "m": ["cmc_entity_metadata ", "entity_metadata", True],
}


def replace_code_segments(replacement_code, tag):
    start_tag = f"// CGSS: {tag}"  # Code Generator Segment Start
    end_tag = f"// CGSE: {tag}"  # Code Generator Segment End

    for file_name in os.listdir("./src"):
        if file_name.endswith(".c") or file_name.endswith(".h"):
            file_path = os.path.join("./src", file_name)

            with open(file_path, "r") as file:
                file_content = file.read()

            pattern = re.compile(
                f"({re.escape(start_tag)}).*?({re.escape(end_tag)})", re.DOTALL
            )
            if not pattern.search(file_content):
                continue

            file_content = pattern.sub(rf"\1\n{replacement_code}\n\2", file_content)

            with open(file_path, "w") as file:
                file.write(file_content)

            return

    raise ValueError(f"didnt find tag {tag}")


def type_def(input_str):
    packet_name, packet_id, symbol_str = input_str.split(";", maxsplit=2)
    symbols = [sym for sym in symbol_str.split(";") if sym != ""]
    return (
        f"typedef struct {{{''.join([f'{type_map[symbol[0]][0]}{symbol[1:]};' for symbol in symbols])}}} {packet_name}_packet;\n\n"
        if symbols
        else ""
    )


def unpack_method(input_str):
    packet_name, packet_id, symbol_str = input_str.split(";", maxsplit=2)
    symbols = [sym for sym in symbol_str.split(";") if sym != ""]
    unpack_method_define = (
        f"{packet_name}_packet unpack_{packet_name}_packet(cmc_buffer *buff)"
    )
    unpack_methods = "".join(
        [
            f"packet.{symbol[1:]}=cmc_buffer_unpack_{type_map[symbol[0]][1]}(buff);"
            for symbol in symbols
        ]
    )
    unpack_method = (
        f"{unpack_method_define} {{{packet_name}_packet packet;{unpack_methods} UNPACK_ERR_HANDELER;return packet;}}\n\n"
        if symbols
        else ""
    )
    return unpack_method


def unpack_method_h(input_str):
    packet_name, packet_id, symbol_str = input_str.split(";", maxsplit=2)
    symbols = [sym for sym in symbol_str.split(";") if sym != ""]
    return (
        f"{packet_name}_packet unpack_{packet_name}_packet(cmc_buffer *buff);\n\n"
        if symbols
        else ""
    )


def send_method(input_str):
    packet_name, packet_id, symbol_str = input_str.split(";", maxsplit=2)
    symbols = [sym for sym in symbol_str.split(";") if sym != ""]
    pack_methods = f"cmc_buffer_pack_varint(buff, CMC_PACKETID_{packet_name.upper()});" + "".join(
        [
            f"cmc_buffer_pack_{type_map[symbol[0]][1]}(buff, {symbol[1:]});"
            for symbol in symbols
        ]
    )
    send_method_define = f"void send_packet_{packet_name}(struct cmc_conn *conn{', ' if symbols else ''} {', '.join([f'{type_map[symbol[0]][0]}{symbol[1:]}' for symbol in symbols])})"
    send_method = f"{send_method_define} {{cmc_buffer *buff = cmc_buffer_init();{pack_methods}  ERR_CHECK(return;); cmc_conn_send_packet(conn, buff);}}\n\n"
    return send_method


def send_method_h(input_str):
    packet_name, packet_id, symbol_str = input_str.split(";", maxsplit=2)
    symbols = [sym for sym in symbol_str.split(";") if sym != ""]
    return f"void send_packet_{packet_name}(struct cmc_conn *conn{',' if symbols else ''} {', '.join([f'{type_map[symbol[0]][0]}{symbol[1:]}' for symbol in symbols])});\n\n"


def comment_filter(raw):
    out = ""
    comment = False
    for token in raw:
        if token == "#":
            comment = True

        if comment:
            if token == "\n":
                out += token
                comment = False
            continue

        out += token
    return out


def packet_ids(mc_packet_exps):
    packet_states = []
    for exp in mc_packet_exps:
        a = "_".join(exp.split("_")[:2])
        if a not in packet_states:
            packet_states.append(a)

    code = ""
    for state in packet_states:
        code += f"enum packetids_{state} {{"
        for exp in mc_packet_exps:
            if exp.startswith(state):
                code += f"CMC_PACKETID_{state.upper()}_{'_'.join(exp.split('_')[2:]).split(';')[0].upper()} = {exp.split(';')[1]},"
        code += "};"

    return code

def should_have_free_method(exp):
    packet_name, packet_id, symbol_str = exp.split(";", maxsplit=2)
    symbols = [sym for sym in symbol_str.split(";") if sym != ""]
    if [True for sym in symbols if type_map[sym[0]][2]]:
        return True
    return False

def free_method(exp):
    packet_name, packet_id, symbol_str = exp.split(";", maxsplit=2)
    symbols = [sym for sym in symbol_str.split(";") if sym != ""]
    if not should_have_free_method(exp):
        return ""

    code = f"void cmc_free_{packet_name}_packet({packet_name}_packet packet) {{"
    for sym in symbols:
        if type_map[sym[0]][2]:
            code += f"free_{type_map[sym[0]][1]}(packet.{sym[1:]});"
    code += "}"
    return code

def loop_handler(exp):
    packet_name, packet_id, symbol_str = exp.split(";", maxsplit=2)
    short_packet_name = "_".join(packet_name.split("_")[2:])
    return f"""case CMC_PACKETID_S2C_PLAY_{short_packet_name.upper()}: {{
        if (!conn->on_packet.{short_packet_name})
          goto unhandeled_packet;
        S2C_play_{short_packet_name}_packet data =
            ERR_ABLE(unpack_S2C_play_{short_packet_name}_packet(packet), goto err_free_packet;);
        conn->on_packet.{short_packet_name}(data, conn);
        {f'cmc_free_S2C_play_{short_packet_name}_packet(data);' if should_have_free_method(exp) else ''}
        break;
    }}"""

def main():
    with open("packets/packets.txt", "r") as f:
        raw = f.read()

    raw = comment_filter(raw)

    raw = raw.replace(" ", "").split("\n")
    mc_packet_exps = []
    for l in raw:
        if not l == "":
            mc_packet_exps.append(l)

    # packet unpack methods
    replace_code_segments(
        "".join([unpack_method(mc_packet_exp) for mc_packet_exp in mc_packet_exps]),
        "unpack_methods_c",
    )

    # packet unpack methods header
    replace_code_segments(
        "".join([unpack_method_h(mc_packet_exps) for mc_packet_exps in mc_packet_exps]),
        "unpack_methods_h",
    )

    # packet send methods
    replace_code_segments(
        "".join([send_method(mc_packet_exp) for mc_packet_exp in mc_packet_exps]),
        "send_methods_c",
    )

    # packet send methods header
    replace_code_segments(
        "".join([send_method_h(mc_packet_exp) for mc_packet_exp in mc_packet_exps]),
        "send_methods_h",
    )

    # packet id to string
    replace_code_segments( # case PACKET_ID(0x00, CONN_STATE_HANDSHAKE, DIRECTION_C2S): return "C2S_handshake_handshake";
        "".join(
            [
                f"case PACKET_ID({mc_packet_exp.split(';')[1]}, CMC_CONN_STATE_{mc_packet_exp.split(';')[0].split('_')[1].upper()}, CMC_DIRECTION_{mc_packet_exp.split(';')[0].split('_')[0].upper()}): return \"{mc_packet_exp.split(';')[0]}\";"
                for mc_packet_exp in mc_packet_exps
            ]
        ),
        "packet_id_to_string",
    )

    # packet ids
    replace_code_segments(packet_ids(mc_packet_exps), "packet_ids")

    # type defs
    replace_code_segments(
        "".join([type_def(mc_packet_exp) for mc_packet_exp in mc_packet_exps]),
        "packet_types",
    )

    replace_code_segments(
        "\n".join([free_method(sym) for sym in mc_packet_exps]), "free_methods_c"
    )

    replace_code_segments(
        "\n".join([f"void cmc_free_{exp.split(';', maxsplit=2)[0]}_packet({exp.split(';', maxsplit=2)[0]}_packet packet);" for exp in mc_packet_exps if should_have_free_method(exp)]), "free_methods_h"
    )

    os.system("clang-format -i ./src/*.c ./src/*.h")
    # The Zen of Python, by Tim Peters
    #
    # Beautiful is better than ugly.
    # ...

    # i mean there is no zen of c ...


if __name__ == "__main__":
    main()