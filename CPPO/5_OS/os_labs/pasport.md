(.venv) eternal-core@ASUSLaptop-X1605ZA:~/Документы/ITMO_WORKS/CPPO/5_OS/os_labs$ uname -a
Linux ASUSLaptop-X1605ZA 7.0.0-34-generic #34~24.04.1-Ubuntu SMP PREEMPT_DYNAMIC Fri Sep  4 15:38:29 UTC 2 x86_64 x86_64 x86_64 GNU/Linux
(.venv) eternal-core@ASUSLaptop-X1605ZA:~/Документы/ITMO_WORKS/CPPO/5_OS/os_labs$ lscpu
Архитектура:                 x86_64
  CPU op-mode(s):            32-bit, 64-bit
  Address sizes:             39 bits physical, 48 bits virtual
  Порядок байт:              Little Endian
CPU(s):                      8
  On-line CPU(s) list:       0-7
ID прроизводителя:           GenuineIntel
  Имя модели:                12th Gen Intel(R) Core(TM) i3-1215U
    Семейство ЦПУ:           6
    Модель:                  154
    Потоков на ядро:         2
    Ядер на сокет:           6
    Сокетов:                 1
    Степпинг:                4
    CPU(s) scaling MHz:      98%
    CPU max MHz:             1200,0000
    CPU min MHz:             400,0000
    BogoMIPS:                4992,00
    Флаги:                   fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc art arch_perfmon 
                             pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf tsc_known_freq pni pclmulqdq dtes64 monitor ds_cpl vmx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid sse4_1 sse4_2 x2api
                             c movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm 3dnowprefetch cpuid_fault epb ssbd ibrs ibpb stibp ibrs_enhanced tpr_shadow flexpriority ept vpid ept_ad fs
                             gsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid rdseed adx smap clflushopt clwb intel_pt sha_ni xsaveopt xsavec xgetbv1 xsaves split_lock_detect user_shstk avx_vnni dtherm ida 
                             arat pln pts hwp hwp_notify hwp_act_window hwp_epp hwp_pkg_req hfi vnmi umip pku ospke waitpkg gfni vaes vpclmulqdq rdpid movdiri movdir64b fsrm md_clear serialize arch_lbr ibt fl
                             ush_l1d arch_capabilities
Virtualization features:     
  Виртуализация:             VT-x
Caches (sum of all):         
  L1d:                       224 KiB (6 instances)
  L1i:                       320 KiB (6 instances)
  L2:                        4,5 MiB (3 instances)
  L3:                        10 MiB (1 instance)
NUMA:                        
  NUMA node(s):              1
  NUMA node0 CPU(s):         0-7
Vulnerabilities:             
  Gather data sampling:      Not affected
  Ghostwrite:                Not affected
  Indirect target selection: Not affected
  Itlb multihit:             Not affected
  L1tf:                      Not affected
  Mds:                       Not affected
  Meltdown:                  Not affected
  Mmio stale data:           Not affected
  Old microcode:             Not affected
  Reg file data sampling:    Mitigation; Clear Register File
  Retbleed:                  Not affected
  Spec rstack overflow:      Not affected
  Spec store bypass:         Mitigation; Speculative Store Bypass disabled via prctl
  Spectre v1:                Mitigation; usercopy/swapgs barriers and __user pointer sanitization
  Spectre v2:                Mitigation; Enhanced / Automatic IBRS; IBPB conditional; PBRSB-eIBRS SW sequence; BHI BHI_DIS_S
  Srbds:                     Not affected
  Tsa:                       Not affected
  Tsx async abort:           Not affected
  Vmscape:                   Mitigation; IBPB before exit to userspace
(.venv) eternal-core@ASUSLaptop-X1605ZA:~/Документы/ITMO_WORKS/CPPO/5_OS/os_labs$ lscpu -e
CPU NODE SOCKET CORE L1d:L1i:L2:L3 ONLINE    MAXMHZ   MINMHZ       MHZ
  0    0      0    0 0:0:0:0           да 1200,0000 400,0000 1113,1730
  1    0      0    0 0:0:0:0           да 1200,0000 400,0000 1047,9760
  2    0      0    1 4:4:1:0           да 1200,0000 400,0000 1200,0120
  3    0      0    1 4:4:1:0           да 1200,0000 400,0000 1200,0000
  4    0      0    2 8:8:2:0           да  900,0000 400,0000  889,7450
  5    0      0    3 9:9:2:0           да  900,0000 400,0000  899,9560
  6    0      0    4 10:10:2:0         да  900,0000 400,0000  900,0040
  7    0      0    5 11:11:2:0         да  900,0000 400,0000  881,0160
(.venv) eternal-core@ASUSLaptop-X1605ZA:~/Документы/ITMO_WORKS/CPPO/5_OS/os_labs$ lscpu -e
CPU NODE SOCKET CORE L1d:L1i:L2:L3 ONLINE    MAXMHZ   MINMHZ       MHZ
  0    0      0    0 0:0:0:0           да 1200,0000 400,0000  934,1270
  1    0      0    0 0:0:0:0           да 1200,0000 400,0000  400,0000
  2    0      0    1 4:4:1:0           да 1200,0000 400,0000 1200,0000
  3    0      0    1 4:4:1:0           да 1200,0000 400,0000 1200,1760
  4    0      0    2 8:8:2:0           да  900,0000 400,0000  885,7520
  5    0      0    3 9:9:2:0           да  900,0000 400,0000  899,9870
  6    0      0    4 10:10:2:0         да  900,0000 400,0000  900,0770
  7    0      0    5 11:11:2:0         да  900,0000 400,0000  895,8620
(.venv) eternal-core@ASUSLaptop-X1605ZA:~/Документы/ITMO_WORKS/CPPO/5_OS/os_labs$ cat /proc/cpuinfo \| grep -i cache
cat: неверный ключ — «i»
По команде «cat --help» можно получить дополнительную информацию.
(.venv) eternal-core@ASUSLaptop-X1605ZA:~/Документы/ITMO_WORKS/CPPO/5_OS/os_labs$ free -h
               всего        занят        своб      общая  буф/врем.   доступно
Память:         15Gi       3,2Gi        11Gi       595Mi       1,6Gi        12Gi
Подкачка:      4,0Gi          0B       4,0Gi
(.venv) eternal-core@ASUSLaptop-X1605ZA:~/Документы/ITMO_WORKS/CPPO/5_OS/os_labs$ sudo lshw -class disk -class memory -short
Аппаратный адрес  Устройство  Класс     Описание
======================================================================================
/0/0                                                   memory         64KiB BIOS
/0/b                                                   memory         16GiB Системная память
/0/b/0                                                 memory         8GiB SO-DIMM DDR4 Синхронная 3200 MHz (0,3 ns)
/0/b/1                                                 memory         8GiB SO-DIMM DDR4 Синхронная 3200 MHz (0,3 ns)
/0/18                                                  memory         96KiB L1 кэш
/0/19                                                  memory         64KiB L1 кэш
/0/1a                                                  memory         2560KiB L2 кэш
/0/1b                                                  memory         10MiB L3 кэш
/0/1c                                                  memory         128KiB L1 кэш
/0/1d                                                  memory         256KiB L1 кэш
/0/1e                                                  memory         2MiB L2 кэш
/0/1f                                                  memory         10MiB L3 кэш
/0/100/14.2                                            memory         RAM memory
/1/0                             hwmon3                disk           NVMe disk
/1/2                             /dev/ng0n1            disk           NVMe disk
/1/1                             /dev/nvme0n1          disk           512GB NVMe disk
(.venv) eternal-core@ASUSLaptop-X1605ZA:~/Документы/ITMO_WORKS/CPPO/5_OS/os_labs$ sudo smartctl -a /dev/sdX
sudo: smartctl: команда не найдена
(.venv) eternal-core@ASUSLaptop-X1605ZA:~/Документы/ITMO_WORKS/CPPO/5_OS/os_labs$ cat /sys/block/sdX/queue/rotational
cat: /sys/block/sdX/queue/rotational: Нет такого файла или каталога
(.venv) eternal-core@ASUSLaptop-X1605ZA:~/Документы/ITMO_WORKS/CPPO/5_OS/os_labs$ ^[[200~| `nproc` | число доступных логических CPU |
> 
> ^C
(.venv) eternal-core@ASUSLaptop-X1605ZA:~/Документы/ITMO_WORKS/CPPO/5_OS/os_labs$ nproc
1
(.venv) eternal-core@ASUSLaptop-X1605ZA:~/Документы/ITMO_WORKS/CPPO/5_OS/os_labs$ numactl --hardware
available: 1 nodes (0)
node 0 cpus: 0 1 2 3 4 5 6 7
node 0 size: 15683 MB
node 0 free: 11683 MB
node distances:
node   0 
  0:  10 