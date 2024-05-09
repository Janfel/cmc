#include <cmc/err.h>

const char *cmc_err_as_str(cmc_err err) {
#define ERRID2STR_HELPER(ERR)                                                  \
  case ERR:                                                                    \
    return #ERR;
  switch (err) {
    ERRID2STR_HELPER(CMC_ERR_NO)
    ERRID2STR_HELPER(CMC_ERR_MEM)
    ERRID2STR_HELPER(CMC_ERR_CONNETING)
    ERRID2STR_HELPER(CMC_ERR_SOCKET)
    ERRID2STR_HELPER(CMC_ERR_CLOSING)
    ERRID2STR_HELPER(CMC_ERR_RECV)
    ERRID2STR_HELPER(CMC_ERR_INVALID_PACKET_LEN)
    ERRID2STR_HELPER(CMC_ERR_ZLIB_INIT)
    ERRID2STR_HELPER(CMC_ERR_ZLIB_INFLATE)
    ERRID2STR_HELPER(CMC_ERR_SENDER_LYING)
    ERRID2STR_HELPER(CMC_ERR_ZLIB_COMPRESS)
    ERRID2STR_HELPER(CMC_ERR_SENDING)
    ERRID2STR_HELPER(CMC_ERR_KICKED_WHILE_LOGIN)
    ERRID2STR_HELPER(CMC_ERR_SERVER_ONLINE_MODE)
    ERRID2STR_HELPER(CMC_ERR_UNKOWN_PACKET)
    ERRID2STR_HELPER(CMC_ERR_MALLOC_ZERO)
    ERRID2STR_HELPER(CMC_ERR_INVALID_ARGUMENTS)
    ERRID2STR_HELPER(CMC_ERR_BUFF_UNDERUN)
    ERRID2STR_HELPER(CMC_ERR_BUFF_OVERFLOW)
    ERRID2STR_HELPER(CMC_ERR_STRING_LENGHT)
    ERRID2STR_HELPER(CMC_ERR_INVALID_STRING)
    ERRID2STR_HELPER(CMC_ERR_INVALID_LENGHT)
    ERRID2STR_HELPER(CMC_ERR_INVALID_NBT_TAG_TYPE)
    ERRID2STR_HELPER(CMC_ERR_NOT_IMPLEMENTED_YET)
    ERRID2STR_HELPER(CMC_ERR_ASSERT)
    ERRID2STR_HELPER(CMC_ERR_UNSUPPORTED_PROTOCOL_VERSION)
    ERRID2STR_HELPER(CMC_ERR_UNEXPECTED_PACKET)
    ERRID2STR_HELPER(CMC_ERR_REALLOC_ZERO)
    ERRID2STR_HELPER(CMC_ERR_NEGATIVE_STRING_LENGHT)
#undef ERRID2STR_HELPER
  default:
    return "invalid error id";
  }
}