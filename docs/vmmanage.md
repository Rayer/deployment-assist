##vmmanage command

*SCG Deployment Utilities*

stynax : `vmmanage [show | create | delete | setup | stop | start | syslink | purge_db | purge_storage]`

###show
Show current managed SCG(s) status.

```
kvm01 :: ~ » vmmanage show
Online :
[ 17][running    ]:	maxlee_01                     	172.17.60.71    	10.2.6.5        	 vscg	525@ml
[ 27][running    ]:	J-VSZ-ML                      	None            	None            	 vscg	297@ml
[ 28][running    ]:	J-VSZ-ML-528                  	None            	None            	 vscg	528@ml
[ 48][running    ]:	shoiML                        	172.17.60.80    	10.2.5.185      	  scg	530@ml
[ 57][running    ]:	shoi31                        	172.17.60.142   	10.2.5.167      	  scg	490@sz3.1.1

Offline :
[  -][unmanaged  ]:	dora_3.4_private              	 None	None@None
[  -][unmanaged  ]:	dora_scg_34_int_2373          	 None	None@None
```

###create

Create SCG VMs instance from repository.

```
kvm01 :: ~ » vmmanage create
VM Name : R-Test-SCG
setlocale: No such file or directory
Supported Branches :
0 : Private Build
1 : sz3.1.1
2 : sz3.1.2
3 : ml
4 : sz3.5-gui
5 : sz3.1
6 : sz3.2
7 : sz3.2.1
Select a branch : 3
SCG Type - 1. SCG 2. SCGE 3. vSCG : 1
Enter version or 'i' for version list : i
Available versions for scg of 3.4.0.0.*:
3 9 10 13 14 278 280 281 283 285 288 289 290 291 292 293 294 295 296 297 298 299 300 301 302 303 304 305 306 307 308 309 310 311 312 313 314 315 316 317 318 319 320 321 322 323 324 325 326 327 328 329 330 331 332 333 334 335 336 337 338 342 350 351 352 353 355 358 359 360 361 362 364 365 366 367 368 369 370 371 372 373 374 375 376 377 378 379 380 381 382 383 384 385 386 387 388 389 390 391 392 393 394 395 396 397 398 399 400 401 402 403 404 405 406 407 408 409 410 411 412 413 414 415 416 417 418 419 420 421 422 423 426 427 428 429 430 431 432 434 435 436 437 438 439 440 441 442 443 444 445 446 447 448 449 450 451 452 453 454 455 456 457 458 459 460 461 462 463 464 465 466 467 468 469 470 471 472 473 474 475 476 477 478 479 480 481 482 483 484 485 486 487 488 489 490 493 494 495 496 497 498 499 500 501 503 504 505 506 507 508 509 510 511 512 513 514 515 516 517 518 519 520 521 522 523 525 527 528 529 530 531 532 533
Enter version or 'i' for version list : 533
Allocate memory [16] :
Enable IPv6? [y/N]:
IPv6 is disabled!
Init with scg (name: R-Test-SCG) ml@533
Handling SCG...

```

Currently it only supported for SCG(3nic) / vSZ(3nic/High Scale Profile) / SZ104 (1nic)

###delete

Delete a VM. if name is not provided, it will have a interactive shell for selecting.

Delete command consumes both VM name and VM Running ID.

```
kvm01 :: ~ » vmmanage delete R-Test-SCG
Domain R-Test-SCG destroyed

Domain R-Test-SCG has been undefined

deleting file : /kvm_images/R-Test-SCG.qcow2
```

###setup

Internal use command. It will start a responsive server(for `vmcluster`) and do necessery symbolic link. 

It is recommended to exeute this command after updating, for example : `git update && vmmanage setup`

###stop

Stop a managed VM. It consumes both Running ID or VM Name.

###start

Start a managed VM.

###syslink

Do necessery symbolic link. It will symbolic-link these files under /usr/bin : 

```
symbolic_link_map = (
    ('deploy.py', '/usr/bin/deploy'),
    ('version_list.py', '/usr/bin/version_list'),
    ('sesame2.py', '/usr/bin/sesame2'),
    ('vmmanage.py', '/usr/bin/vmmanage'),
    ('vmcluster.py', '/usr/bin/vmcluster'),
    ('deploy_private.py', '/usr/bin/deploy_private')

)
```
For locally usage of `vmcluster` and `deploy_private`, it is also recommended to run `sudo ./vmmanage.py syslink`

###purge_db

Purge Database. Sometimes some instance will be deleted by other KVM management application like virt-manager by user, it can purge VM status databse to repair such issue.

###purge_storage

Purge images. Sometime someone will remove instance by other KVM management application and **forget to remove image**, it can fix such issue.

It will remove every untethered images in image directory.