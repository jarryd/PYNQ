#   Copyright (c) 2016, Xilinx, Inc.
#   All rights reserved.
# 
#   Redistribution and use in source and binary forms, with or without 
#   modification, are permitted provided that the following conditions are met:
#
#   1.  Redistributions of source code must retain the above copyright notice, 
#       this list of conditions and the following disclaimer.
#
#   2.  Redistributions in binary form must reproduce the above copyright 
#       notice, this list of conditions and the following disclaimer in the 
#       documentation and/or other materials provided with the distribution.
#
#   3.  Neither the name of the copyright holder nor the names of its 
#       contributors may be used to endorse or promote products derived from 
#       this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
#   THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
#   PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
#   EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#   OR BUSINESS INTERRUPTION). HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
#   WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
#   OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
#   ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__author__      = "Anurag Dubey"
__copyright__   = "Copyright 2016, Xilinx"
__email__       = "pynq_support@xilinx.com"

import os
import cffi
import resource

ffi = cffi.FFI()

ffi.cdef("""
static uint32_t xlnkBufCnt = 0;
uint32_t cma_mmap(uint32_t phyAddr, uint32_t len);
uint32_t cma_munmap(void *buf, uint32_t len);
void *cma_alloc(uint32_t len, uint32_t cacheable);
uint32_t cma_get_phy_addr(void *buf);
void cma_free(void *buf);
uint32_t cma_pages_available();
void _xlnk_reset();
""")

libxlnk = ffi.dlopen("/usr/lib/libxlnk_cma.so")

class xlnk:

    def __init__(self):
        self.bufmap = {}

    def __del__(self):
        for key in self.bufmap.keys():
            libxlnk.cma_free(key)
    
    def __check_buftype(self, buf):
        if type(buf) != type(ffi.new("char *")) or\
          type(buf) != type(ffi.new_handle('void')):
            raise RuntimeError("Unknown buffer type")
        
    def cma_alloc(self, length, cacheable = 0):
        buf = libxlnk.cma_alloc(length, cacheable)
        if buf == ffi.NULL:
            raise RuntimeError("Failed to allocate Memory!")
        bufmap[buf] = length
        return buf

    def cma_get_buffer_object(self, buf):
        self.__check_buftype(buf)
        return(memoryview(ffi.buffer(buf)))
    
    def cma_cast(self, type, data):
        return ffi.cast(type+"*", data)
      
    def cma_free(self, buf):
        if buf in self.bufmap:
            self.bufmap.pop(buf, None)
        self.__check_buftype(buf)
        libxlnk.cma_free(buf)
    
    def cma_stats(self):
        stats = {}
        free_pages = libxlnk.cma_pages_available()
        stats['CMA Memory Available'] = resource.getpagesize() * free_pages
        memused = 0
        for key in self.bufmap:
            memused += self.bufmap[key]
        stats['CMA Memory Usage'] = memused
        stats['Buffer Count'] = len(self.bufmap)
        return stats

    def xlnk_reset(self):
        libxlnk._xlnk_reset();'_cffi_backend.CDataOwn'