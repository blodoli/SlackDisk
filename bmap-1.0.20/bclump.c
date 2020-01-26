/* bclump.c: collect numbers from bmap
 *
 * Maintained 19^H^H2000 by Daniel Ridge in support of:
 *   Scyld Computing Corporation.
 *
 * The maintainer may be reached as newt@scyld.com or C/O
 *   Scyld Computing Corporation
 *   410 Severn Ave, Suite 210
 *   Annapolis, MD 21403
 *
 * Contributed by Robert J. Hergert
 */

/*
 * Sample input:
 *
 * 4
 * 5
 * 6
 * 7
 * 8
 * 9
 * 11
 * 12
 * 20
 * 21
 * 23
 * 24
 * 25
 * 17
 * 18
 * 19
 * 0
 * 1
 * 2
 * 3
 * 8
 * 9
 * 10
 * 11
 * 12
 *
 * Sample output:
 *
 * 0-12
 * 17-21
 * 23-25
 *
 * (Notice that the number ranges are sorted and unique.)
 *
 * DISCLAIMER:
 *    This application was written wihtin the Red Hat 6.0 Operating System.
 * This application compiles and runs with the following GCC version 
 * information: egcs-2.91.66 19990314/Linux (egcs-1.1.2 release).
 * the author makes no claim that this application will produce the same results
 * under any other operating system or using a different complier. However, it
 * should work under any version of UNIX and using any standard C compiler.
 */

/* Libraries */
#include "config.h"

#include <stdio.h>
#include <stdlib.h>
#include <strings.h>
#include <stddef.h>
#include <signal.h>
#include <errno.h>
#include <string.h>

#include <mft.h>
#include "bmap.h"

/* Structure for the tree */

struct tree_node {
	struct tree_node *parent;
	long long upper;
	long long lower;
	struct tree_node *rt;
	struct tree_node *lt;
};

/* Structure for the queue */

struct List{
	struct List *next;
	struct tree_node *data;
};

/* Function Prototypes */

void encoder_signal(int signum);
void create_list(struct tree_node *node, struct List *list);
void place_node (struct tree_node *node, struct tree_node *new);
struct tree_node *init_node(long long lower, long long upper);
void minimize (struct tree_node *node);
void dumptree (FILE *f,struct tree_node *node);

/* Declared globally for the signal handling, this is the root node of the
 * tree that will be written to stdout. */

struct tree_node *root = NULL;

/* Allocate memory for a tree node and initialize it */

struct tree_node *init_node (long long lower, long long upper) {

	struct tree_node *retval;

	if((retval = (struct tree_node *)malloc(sizeof(struct tree_node))) 
	   == NULL){
		/* Error handling, exit the program if out of memory. */
		fprintf(stderr, "ERROR: Out of Memory: Exiting.");
		exit(1);
	}
	/* Initialization */
	retval->parent = NULL;
	retval->lower = lower;
	retval->upper = upper;
	retval->rt = NULL;
	retval->lt = NULL;
	return(retval);
}

/* Minimize the RLE tree. When a range is changed make sure the nodes
 * in the sub-tree do not belong in the range
 */
void minimize (struct tree_node *node) {

	struct List *list, *tmp;

	if(node->lt == NULL && node->rt == NULL){
		return;
	}
	/* Allocate the head of the list */
	if((list=malloc(sizeof(struct List))) == NULL) {
		fprintf(stderr, "Out of Memory Error. Exiting.\n");
		exit(1);
	}
	/* initialize the head */
	list->data = NULL;
	list->next = NULL;

	/* Create a queue from the sub tree */
	create_list(node, list);

	/* Error checking */
	if(list->data != node){
	       fprintf(stderr, "Something strange is afoot at the circle K!\n");
	}
	tmp = list;
	if(tmp->data != node){
		fprintf(stderr, "dammit\n");
	}
	/* Initialize the root node for the minimization */
	node->lt = NULL;
	node->rt = NULL;
	list = list->next;

	list = tmp->next;

	while(list != NULL && list->data != NULL){
	/* initialize the data for placement */
		list->data->parent = NULL;
		list->data->lt = NULL;
		list->data->rt = NULL;
	/* place the node */
		place_node(node, list->data);
	/* get the next element of the queue */
		list = list->next;
	}
	/* destroy the list */
	while(tmp != NULL){
		list = tmp;
		tmp = tmp->next;
		free(list);
	}
}
	
void place_node (struct tree_node *node, struct tree_node *new) {

/* placement of a node in the tree */

	struct tree_node *curr_node = node;
	int placed = 0;

/* Mostly alot of comparison for placing a range in the tree
 * notice that when a node's range is changed by an insertion
 * into the tree minimize is called.
 */
	while(placed != 1){
		if (new->upper <= curr_node->upper) {
			if (new->lower >= curr_node->lower){
			/* Node is wihtin an existing range so it can be
			 * deleted. */
				free(new);
				placed = 1;
			} else if ((new->upper >= curr_node->lower) &&
				(new->lower <= curr_node->lower)){
					curr_node->lower = new->lower;
					minimize(curr_node);
					free(new);
					placed = 1;
			} else if (new->upper < curr_node->lower){
				if(new->upper == (curr_node->lower - 1)){
					curr_node->lower = new->lower;
					free(new);
					minimize(curr_node);
					placed = 1;
				} else if (curr_node->rt != NULL) {
					curr_node=curr_node->rt;
				} else {
					new->parent = curr_node;
					curr_node->rt = new;
					placed = 1;
				}
			}
		} else if (new->upper > curr_node->upper) {
			if(new->lower == (curr_node->upper + 1)){
				curr_node->upper = new->upper;
				free(new);
				minimize(curr_node);
				placed = 1;
			} else if (new->lower <= curr_node->lower){
				curr_node->lower = new->lower;
				curr_node->upper = new->upper;
				free(new);
				minimize(curr_node);
				placed = 1;
			} else if (new->lower < curr_node->upper){
				curr_node->upper = new->upper;
				free(new);
				minimize(curr_node);
				placed=1;
			} else if (new->lower > curr_node->upper){
				if(curr_node->lt != NULL){
					curr_node = curr_node->lt;
				} else {
					new->parent = curr_node;
					curr_node->lt = new;
					placed = 1;
				}
			}	
		}
	}
}

void 
dumptree(FILE *f,struct tree_node *node)
{
/* recusive function for traversing the tree, simply prints ranges to stdout */


	if(node != NULL){
		dumptree(f,node->rt);
		fprintf(f,"%Ld-%Ld\n", node->lower, node->upper);
		dumptree(f,node->lt);
	}
}

void
create_list(struct tree_node *node, struct List *list)
{

/* Create a queue for data minimization. This is similar to the
 * tree traversal, but it does this in a different fashion to avoid
 * an infinite loop of recreating the same sub tree.
 */
	struct List *new;

	if(node != NULL){
		if((new = malloc(sizeof(struct List))) == NULL){
			printf("Out of Memory Error. Exiting.\n");
			exit(1);
		} else {
			new->data = NULL;
			new->next = NULL;
			list->data = node;
			list->next = new;
		}
		create_list(node->rt, new);
		while(new->next != NULL){
			new = new->next;
		}
		create_list(node->lt, new);
	}
}


enum doc_modes {BCLUMP_VERSION,BCLUMP_HELP,BCLUMP_MAN,BCLUMP_SGML};

static struct mft_option options[]={
	{"doc","autogenerate document ...",
	 MOT_VENUM|MOF_SILENT,
	 MO_VENUM_CAST{
	   {"version","display version and exit",
	    0,MO_INT_CAST(BCLUMP_VERSION)
	   },
	   {"help","display options and exit",
	    0,MO_INT_CAST(BCLUMP_HELP)
	   },
	   {"man","generate man page and exit",
	    0,MO_INT_CAST(BCLUMP_MAN)
	   },
	   {"sgml","generate SGML invokation info",
	    0,MO_INT_CAST(BCLUMP_SGML)
	   },
	   {NULL,NULL,0,MO_CAST(NULL)}
	 }
	},
	{"infile","read bmap input from ...",
	 MFT_OPTION_TYPE_FILENAME,NULL},
	{"outfile","write condensed output to ...",
	 MFT_OPTION_TYPE_FILENAME,NULL},
	{NULL,NULL,0,NULL}
};

static struct mft_info bclump_info={
  "bclump",
  "collect and compact bmap mappings",
  AUTHOR,
  VERSION "( " BUILD_DATE ")",
  options
};

static char *outfile=NULL;	
int
main (int argc, char **argv)
{
/* Variable declaration */
int bgn = 1;
long long begin = 0, in_num = 0, hold = 0;
struct tree_node *newnode;
FILE *pipe;
char *infile=NULL;

int optval,option_index;
union option_arg option_arg;

	/* parse some command-line arguments */ 
	option_index=0;
	optval=0;
	while(optval != -EINVAL && (optval=mft_getopt(argc,argv,options,MO_REMOVE,&option_index,(void *)&option_arg)) != -ENOENT)
	{
		switch(optval)
		{
		case 0: /* doc */
			switch(option_arg.a_enum)
			{
			case BCLUMP_VERSION:
				mft_display_version(stdout,&bclump_info);
				break;
			case BCLUMP_HELP:
				mft_display_version(stdout,&bclump_info);
				mft_display_help(stdout,&bclump_info,NULL);
				break;
			case BCLUMP_MAN:
				mft_display_man(stdout,BUILD_DATE,1,&bclump_info,NULL);
				break;
			case BCLUMP_SGML:
				mft_display_sgml(stdout,&bclump_info,NULL);
			}
			mft_log_exit();
			exit(0);
	       		break;
		case 1: /* infile */
			/* dash means stdin */
			if(strcmp(option_arg.a_filename,"-"))
			  infile=strdup(option_arg.a_filename);
			break;
	        case 2: /* outfile */
		  	/* dash means stdout */
		  	if(strcmp(option_arg.a_filename,"-"))
			  outfile=strdup(option_arg.a_filename);
			break;
		}
	}
	
	/* install a signal handler
	 * (default behavior will be to dump tree on HUP
         * exit the application.
	 */	 

	signal(SIGHUP,encoder_signal);

	/* Start an infinite loop for reading the pipe */

	while(1)
	{
		/* Open the pipe for reading */
	  	if(infile)
		  pipe = fopen(infile, "r");
		else
		  pipe=stdin;

		/* Error checking */
		/* if the pipe was not opened we exit the application. */

		if(pipe == NULL){
			printf("could not open pipe\n");
			exit(1);
		}

		/* Read numbers until end of file. */
		while(fscanf(pipe,"%Ld\n",&in_num) != EOF)
		{
			/* initalize numbers in the beginning */

			if(bgn == 1)
			{
				begin = in_num;
				hold = in_num;
				bgn = 0;
			} else {

				/* if the current number is greater than the 
				 * last number by one hold on to it */

				if(in_num == (hold + 1))
				{
					hold = in_num;
				} else {

					/* if the number is not in sequence initalize a
					 * new node  */

					newnode=init_node(begin, hold);
					/* initialize the root node if it is still NULL*/
					if(root == NULL)
					{
						root = newnode;
					} else {
					/* oterwise place the node in the tree */
					  place_node(root, newnode);
					}
					/* initialize the range to the new number */
					begin = in_num;
					hold = in_num;
				}
			}
		}

		newnode = init_node(begin, hold);
		if(root == NULL){
			root = newnode;
		} else {
			place_node(root, newnode);
		}

		/* Done reading on the pipe for now so we close it */

		if(infile)
		  fclose(pipe);
	}
}

void
encoder_signal(int signum)
{
FILE *out_f;
/* Catch the signal from the OS and print out the tree.
 * Exit the application gracefully */

	if(signum==SIGHUP) {
	  if(outfile)
	    out_f=fopen(outfile,"w");
	  else
	    out_f=stdout;	  

		dumptree(out_f,root);
		exit(0);
	}
}




















