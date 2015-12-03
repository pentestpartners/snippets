#define _FILE_OFFSET_BITS 64

#include <stdio.h>
#include <string.h>
#include <ext2fs/ext2fs.h>

void main(void)
{
   FILE *in;
   struct ext2_super_block superblock;
   long int pos=0;

   in=fopen("innotab.img","rb");
   
   while (!feof(in))
   {
      fseek(in, pos, SEEK_SET);
      memset(&superblock,0,sizeof(superblock));
      fread(&superblock, sizeof(superblock), 1, in);

      if (superblock.s_magic == 0xef53 &&
          superblock.s_state < 3 &&
          superblock.s_errors < 4 &&
          superblock.s_creator_os < 5)
      {
         printf("Possible superblock at %x: %s\n", pos, superblock.s_last_mounted);
      }
      pos++;
   }
} 
